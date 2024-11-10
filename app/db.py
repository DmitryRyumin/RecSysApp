"""
File: db.py
Author: Dmitry Ryumin
Description: Module for working with database in DuckDB.
License: MIT License
"""

import duckdb
import uuid

# Importing necessary components for the Gradio app
from app.config import config_data

# Подключение к базе данных DuckDB
conn = duckdb.connect(
    config_data.Path_APP / config_data.StaticPaths_DB / config_data.AppSettings_DB,
)


# Создание таблиц (если они еще не существуют)
def create_tables():
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        last_name TEXT,
        group_number TEXT,
        role TEXT
    )
    """
    )

    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS courses (
        course_id TEXT PRIMARY KEY,
        label TEXT,
        discipline TEXT,
        department TEXT,
        faculty TEXT,
        campus TEXT,
        level TEXT,
        audience TEXT,
        format TEXT,
        relevance INTEGER
    )
    """
    )

    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS skills (
        course_id TEXT,
        skill TEXT,
        type TEXT,  -- 'relevant' or 'unrelated'
        PRIMARY KEY (course_id, skill)
    )
    """
    )

    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS feedback (
        user_id TEXT,
        message TEXT,
        usefulness INTEGER,
        demand INTEGER,
        convenience INTEGER,
        additional_skills TEXT,
        PRIMARY KEY (user_id)
    )
    """
    )


# Функция для сохранения данных
def save_data(json_data):
    try:
        # Генерация уникального идентификатора для пользователя
        user_id = str(
            uuid.uuid4()
        )  # Использование UUID для создания уникального идентификатора

        user_data = json_data.get("user_data", {})
        conn.execute(
            "INSERT OR REPLACE INTO users (id, last_name, group_number, role) VALUES (?, ?, ?, ?)",
            (
                user_id,
                user_data.get("Фамилия"),
                user_data.get("Номер группы (только для студентов)"),
                user_data.get("Роль или направление"),
            ),
        )

        # Сохранение курсов и навыков
        for group in json_data.get("edu_groups", []):
            label = group.get("label")
            for course in group.get("courses", []):
                course_id = course.get("ID дисциплины:")
                conn.execute(
                    """
                INSERT OR REPLACE INTO courses (course_id, label, discipline, department, faculty, campus, level, audience, format, relevance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        course_id,
                        label,
                        course.get("Дисциплина:"),
                        course.get("Кафедра:"),
                        course.get("Факультет кафедры:"),
                        course.get("Кампус:"),
                        course.get("Уровень обучения:"),
                        course.get("Охват аудитории:"),
                        course.get("Формат изучения:"),
                        int(course.get("Релевантность курса", 0)),
                    ),
                )

                # Сохранение навыков
                for skill in course.get("Получаемые навыки (релевантные)", []):
                    conn.execute(
                        "INSERT OR IGNORE INTO skills (course_id, skill, type) VALUES (?, ?, 'relevant')",
                        (course_id, skill),
                    )

                for skill in course.get("Получаемые навыки (удаленные)", []):
                    conn.execute(
                        "INSERT OR IGNORE INTO skills (course_id, skill, type) VALUES (?, ?, 'unrelated')",
                        (course_id, skill),
                    )

        # Сохранение обратной связи и дополнительных данных
        feedback_data = json_data.get("additional_ranges", {})
        conn.execute(
            """
        INSERT OR REPLACE INTO feedback (user_id, message, usefulness, demand, convenience, additional_skills)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                json_data.get("user_message"),
                int(feedback_data.get("Полезность", 0)),
                int(feedback_data.get("Востребованность", 0)),
                int(feedback_data.get("Удобство", 0)),
                ", ".join(json_data.get("additional_vacancy_skills", [])),
            ),
        )

        conn.commit()  # Сохранение изменений в базе данных
        return True
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        return False


# Создание таблиц при первом запуске
create_tables()
