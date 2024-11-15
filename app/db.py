"""
File: db.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Module for working with the database in DuckDB.
License: MIT License
"""

import duckdb

# Importing necessary components for the Gradio app
from app.config import config_data

db_path = config_data.Path_APP / config_data.StaticPaths_DB / config_data.AppSettings_DB
db_path.parent.mkdir(parents=True, exist_ok=True)


def create_tables():
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                group_number TEXT,
                role TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                user_id TEXT,
                session_id TEXT,
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
                unrelated_skills TEXT,
                PRIMARY KEY (session_id, course_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                user_id TEXT,
                session_id TEXT PRIMARY KEY,
                message TEXT,
                feedback_comment TEXT,
                utility INTEGER,
                popularity INTEGER,
                comfort INTEGER,
                relevant_vacancy_skills TEXT,
                unrelated_vacancy_skills TEXT,
                additional_vacancy_skills TEXT,
                additional_subject_skills TEXT,
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_time (
                user_id TEXT,
                session_id TEXT PRIMARY KEY,
                start_timestamp TEXT,
                end_timestamp TEXT,
                elapsed_time_ms REAL,
                elapsed_time_s REAL,
                hours INTEGER,
                minutes INTEGER,
                seconds INTEGER,
                milliseconds INTEGER
            )
            """
        )


def save_data(json_data):
    try:

        user_id = json_data.get("user_id")
        if not user_id:
            raise ValueError("Идентификатор пользователя отсутствует в JSON")

        session_id = json_data.get("session_id")

        with duckdb.connect(str(db_path)) as conn:
            user_data = json_data.get("user_data", {})
            conn.execute(
                """
                INSERT OR REPLACE INTO users (user_id, username, group_number, role)
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    user_data.get("Имя пользователя"),
                    user_data.get("Номер группы (только для студентов)"),
                    user_data.get("Роль или направление"),
                ),
            )

            for group in json_data.get("edu_groups", []):
                label = group.get("label")
                for course in group.get("courses", []):
                    course_id = course.get("ID дисциплины")
                    relevant_skills = "; ".join(
                        course.get("Получаемые навыки (релевантные)", [])
                    )
                    unrelated_skills = "; ".join(
                        course.get("Получаемые навыки (удаленные)", [])
                    )

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO courses (
                            user_id, session_id, course_id, label, discipline, department, faculty, campus, level,
                            audience, format, course_number, relevance, relevant_skills, unrelated_skills
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            session_id,
                            course_id,
                            label,
                            course.get("Дисциплина"),
                            course.get("Кафедра"),
                            course.get("Факультет кафедры"),
                            course.get("Кампус"),
                            course.get("Уровень обучения"),
                            course.get("Охват аудитории"),
                            course.get("Формат изучения"),
                            course.get("Курс обучения"),
                            int(course.get("Релевантность курса запросу", 0)),
                            relevant_skills,
                            unrelated_skills,
                        ),
                    )

            feedback_data = json_data.get("additional_ranges", {})
            feedback_comment = json_data.get("feedback", "")
            vacancy_skills = json_data.get("vacancy", {})
            relevant_vacancy_skills = "; ".join(
                vacancy_skills.get(
                    "Требуемые навыки (кликните все неподходящие навыки) (релевантные)",
                    [],
                )
            )
            unrelated_vacancy_skills = "; ".join(
                vacancy_skills.get(
                    "Требуемые навыки (кликните все неподходящие навыки) (удаленные)",
                    [],
                )
            )
            additional_vacancy_skills = "; ".join(
                json_data.get("additional_vacancy_skills", [])
            )

            additional_subjects_skills = "; ".join(
                json_data.get("additional_subjects_skills", [])
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO feedback (
                    user_id, session_id, message, feedback_comment, utility, popularity, comfort,
                    relevant_vacancy_skills, unrelated_vacancy_skills, additional_vacancy_skills, additional_subject_skills
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    session_id,
                    json_data.get("user_message"),
                    feedback_comment,
                    int(feedback_data.get("Полезность", 4)),
                    int(feedback_data.get("Востребованность", 4)),
                    int(feedback_data.get("Удобство", 4)),
                    relevant_vacancy_skills,
                    unrelated_vacancy_skills,
                    additional_vacancy_skills,
                    additional_subjects_skills
                ),
            )

            # Вставка данных времени с новыми полями
            time_data = json_data.get("time", {})
            conn.execute(
                """
                INSERT OR REPLACE INTO session_time (
                    user_id, session_id, start_timestamp, end_timestamp, elapsed_time_ms, elapsed_time_s,
                    hours, minutes, seconds, milliseconds
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    session_id,
                    time_data.get("start_timestamp"),
                    time_data.get("end_timestamp"),
                    float(time_data.get("elapsed_time_ms", 0)),
                    float(time_data.get("elapsed_time_s", 0)),
                    int(time_data.get("hours", 0)),
                    int(time_data.get("minutes", 0)),
                    int(time_data.get("seconds", 0)),
                    int(time_data.get("milliseconds", 0)),
                ),
            )

            conn.commit()

        return True
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        return False


if config_data.AppSettings_QUALITY:
    create_tables()
