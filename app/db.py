"""
File: db.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Module for working with database in DuckDB.
License: MIT License
"""

import duckdb
import os

# Importing necessary components for the Gradio app
from app.config import config_data

# Формирование полного пути
db_path = config_data.Path_APP / config_data.StaticPaths_DB / config_data.AppSettings_DB

# Проверка существования директории и создание ее при необходимости
db_directory = db_path.parent  # Получение родительской директории
if not os.path.exists(db_directory):
    os.makedirs(db_directory)

# Подключение к базе данных DuckDB
conn = duckdb.connect(db_path)


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
        user_id TEXT,
        course_id TEXT,
        label TEXT,
        discipline TEXT,
        department TEXT,
        faculty TEXT,
        campus TEXT,
        level TEXT,
        audience TEXT,
        format TEXT,
        course_number TEXT,
        relevance INTEGER,
        relevant_skills TEXT,
        unrelated_skills TEXT
    )
    """
    )

    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS feedback (
        user_id TEXT,
        message TEXT,
        feedback_comment TEXT,
        utility INTEGER,
        popularity INTEGER,
        comfort INTEGER,
        relevant_vacancy_skills TEXT,
        unrelated_vacancy_skills TEXT,
        additional_vacancy_skills TEXT
    )
    """
    )


# Функция для сохранения данных
def save_data(json_data):
    try:
        # Получение идентификатора пользователя из JSON
        user_id = json_data.get("user_id")
        if not user_id:
            raise ValueError("Идентификатор пользователя отсутствует в JSON")

        # Парсинг данных пользователя
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
                relevant_skills = "; ".join(
                    course.get("Получаемые навыки (релевантные)", [])
                )
                unrelated_skills = "; ".join(
                    course.get("Получаемые навыки (удаленные)", [])
                )

                conn.execute(
                    """
                INSERT INTO courses (
                    user_id, course_id, label, discipline, department, faculty, campus, level, audience, format, course_number, relevance, relevant_skills, unrelated_skills
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        course_id,
                        label,
                        course.get("Дисциплина:"),
                        course.get("Кафедра:"),
                        course.get("Факультет кафедры:"),
                        course.get("Кампус:"),
                        course.get("Уровень обучения:"),
                        course.get("Охват аудитории:"),
                        course.get("Формат изучения:"),
                        course.get("Курс обучения"),
                        int(course.get("Релевантность курса", 0)),
                        relevant_skills,
                        unrelated_skills,
                    ),
                )

        # Сохранение обратной связи и дополнительных данных
        feedback_data = json_data.get("additional_ranges", {})
        feedback_comment = json_data.get("feedback", "")
        vacancy_skills = json_data.get("vacancy", {})
        relevant_vacancy_skills = "; ".join(
            vacancy_skills.get("Навыки вакансии (релевантные)", [])
        )
        unrelated_vacancy_skills = "; ".join(
            vacancy_skills.get("Навыки вакансии (удаленные)", [])
        )
        additional_vacancy_skills = "; ".join(
            json_data.get("additional_vacancy_skills", [])
        )

        conn.execute(
            """
        INSERT INTO feedback (user_id, message, feedback_comment, utility, popularity, comfort, relevant_vacancy_skills, unrelated_vacancy_skills, additional_vacancy_skills)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                json_data.get("user_message"),
                feedback_comment,
                int(feedback_data.get("Полезность", 4)),  # utility
                int(feedback_data.get("Востребованность", 4)),  # popularity
                int(feedback_data.get("Удобство", 4)),  # comfort
                relevant_vacancy_skills,
                unrelated_vacancy_skills,
                additional_vacancy_skills,
            ),
        )

        conn.commit()  # Сохранение изменений в базе данных
        return True
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        return False


# Создание таблиц при первом запуске
create_tables()
