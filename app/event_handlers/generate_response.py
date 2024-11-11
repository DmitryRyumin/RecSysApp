"""
File: generate_response.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to generate response.
License: MIT License
"""

import re
import torch
import polars as pl
import gradio as gr
from gradio import ChatMessage

# Importing necessary components for the Gradio app
from app.config import config_data

from app.data_init import (
    cosine_similarity,
    df_puds_skills,
    df_courses_grades,
    model_manager_sbert,
    skills_extractor,
)
from app.data_utils import (
    get_embeddings,
    filter_unique_items,
    sort_subjects,
    round_if_number,
    format_grade,
)


def create_html_block(label: str, value: str, class_name: str = "info-item") -> str:
    return f"<div class={class_name}><span class='label'>{label}</span> <span class='value'>{value}</span></div>"


def create_html_range(
    label: str, subject_id: str, class_name: str = "subject_relevance"
) -> str:
    return (
        ""
        if not config_data.AppSettings_QUALITY
        else "<div class='range'>"
        f"<label for='{class_name}_{subject_id}'>{label}</label>"
        f"<div class='{class_name}' id='{class_name}_{subject_id}'></div>"
        "</div>"
    )


def determine_edu_level(subject_info: list[str]) -> tuple[str, str]:
    if not subject_info[6] or subject_info[6] in [
        config_data.Settings_PRIORITY[-1],
        config_data.Settings_PRIORITY[-2],
        config_data.EducationLevels_NONE_LEVELS,
    ]:
        edu_level_label = config_data.HtmlContent_LEVELS_EDUCATION_LABEL
        edu_level = config_data.EducationLevels_ALL_LEVELS
    else:
        edu_level_label = config_data.HtmlContent_LEVEL_EDUCATION_LABEL
        edu_level = subject_info[6]

    return edu_level_label, edu_level


def generate_courses_grades(subject_info: list[str]) -> str:
    courses_grades = ""
    has_metrics = False

    for i, index in enumerate(list(range(11, 21))):
        grade_value = subject_info[index]

        match grade_value:
            case "-":
                continue
            case None | "":
                has_metrics = True
                courses_grades += (
                    "<div class='info-courses-grades-error'><span class='label'>"
                    f"{config_data.InformationMessages_COURSES_GRADES_DATA[0]} "
                    f"{config_data.InformationMessages_COURSES_GRADES_NOT_DEFINED[i]} "
                    f"{config_data.InformationMessages_COURSES_GRADES_DATA[1]}"
                    "</span></div>"
                )
            case _:
                has_metrics = True
                courses_grades += create_html_block(
                    f"{config_data.DataframeHeaders_COURSES_GRADES[i]}:",
                    format_grade(grade_value),
                    "info-courses-grades",
                )

    if has_metrics:
        courses_grades = (
            f"<div class='info-item'><span class='label'>{config_data.HtmlContent_COURSES_GRADES}</span></div>"
            f"{courses_grades}"
        )

    return courses_grades


def generate_subject_info(
    subject_info: list[str], edu_level_label: str, edu_level: str
) -> str:
    number_education_block = (
        create_html_block(
            (
                config_data.HtmlContent_NUMBERS_EDUCATION
                if "-" in subject_info[10]
                else config_data.HtmlContent_NUMBER_EDUCATION
            ),
            subject_info[10],
        )
        if subject_info[10] != "-"
        else "<div class='info-number-education-error'><span class='label'>"
        + config_data.InformationMessages_LEVEL_NOT_DEFINED
        + "</span></div>"
    )

    return "".join(
        [
            create_html_range(
                config_data.HtmlContent_SUBJECT_RELEVANCE,
                subject_info[0],
                "subject_relevance",
            ),
            create_html_block(config_data.HtmlContent_SUBJECT_LABEL, subject_info[1]),
            create_html_block(
                config_data.HtmlContent_ID_SUBJECT_LABEL, subject_info[0]
            ),
            create_html_block(
                config_data.HtmlContent_DEPARTMENT_LABEL, subject_info[5]
            ),
            create_html_block(config_data.HtmlContent_FACULTY_LABEL, subject_info[4]),
            create_html_block(config_data.HtmlContent_CAMPUS_LABEL, subject_info[3]),
            create_html_block(edu_level_label, edu_level),
            number_education_block,
            create_html_block(config_data.HtmlContent_AUDIENCE_LABEL, subject_info[8]),
            create_html_block(config_data.HtmlContent_FORMAT_LABEL, subject_info[9]),
            generate_courses_grades(subject_info),
        ]
    )


def generate_skills(
    subject_id: str,
    max_skill_words: int,
) -> str:
    try:
        subject_skills = (
            df_puds_skills.filter(
                pl.col(config_data.DataframeHeaders_RU_ID) == int(subject_id)
            )[0]["LLM_Skills"][0]
            .strip()
            .split(";")
        )

        skills = [
            re.sub(r"[.,;:\s]+$", "", skill.strip()).capitalize()
            for skill in subject_skills
            if len(skill.split()) <= max_skill_words and skill.strip()
        ]

        if not skills:
            raise ValueError

        skills_content = "".join(
            [f"<span class='skill'>{skill}</span>" for skill in skills]
        )
        return (
            f"<div class='info-skills{"-static" if not config_data.AppSettings_QUALITY else ""}'><span class='label'>"
            + config_data.HtmlContent_SKILLS_LABEL
            + "</span> <span class='value'>"
            + f"{skills_content}</span></div>"
        )

    except Exception:
        return (
            "<div class='info-skills-error'><span class='label'>"
            + config_data.InformationMessages_SKILLS_NOT_DEFINED
            + "</span></div>"
        )


def event_handler_generate_response(
    message: str,
    chat_history: list[ChatMessage],
    top_subjects: int,
    max_skill_words: int,
    dropdown_courses_grades: list[str],
) -> tuple[
    gr.Row,
    gr.Textbox,
    gr.Button,
    list[ChatMessage],
    gr.Column,
    gr.Dropdown,
    gr.HTML,
    gr.Textbox,
    gr.Column,
    gr.Button,
]:
    message = message.strip()

    if not message:
        return (
            gr.Row(visible=True),
            gr.Textbox(value=None),
            gr.Button(visible=True),
            chat_history,
            gr.Column(visible=False),
            gr.Dropdown(interactive=False, visible=False),
            gr.HTML(visible=False),
            gr.Textbox(value=None, visible=False),
            gr.Column(visible=False),
            gr.Button(visible=False, interactive=False),
        )

    if config_data.AppSettings_QUALITY:
        top_subjects = config_data.Settings_TOP_SUBJECTS_QUALITY
        max_skill_words = config_data.Settings_MAX_SKILL_WORDS
        dropdown_courses_grades = [config_data.DataframeHeaders_COURSES_GRADES[0]]

    vacancy_embedding = get_embeddings(message, model_manager_sbert.get_current_model())

    with torch.no_grad():
        similarities = (
            cosine_similarity(
                vacancy_embedding, model_manager_sbert.state.puds_embeddings
            )
            .cpu()
            .tolist()
        )
        similarities = [
            (i, j)
            for i, j in zip(
                model_manager_sbert.state.puds_names["names"].to_list(), similarities
            )
        ]

    sorted_subjects = sorted(similarities, key=lambda x: x[1], reverse=True)
    unique_subjects = filter_unique_items(sorted_subjects, top_subjects)

    all_top_items = []

    for subject, similarity in unique_subjects:
        match = next(
            (
                item
                for item in model_manager_sbert.get_puds_data()
                if item.get(config_data.DataframeHeaders_RU_SUBJECTS[0]) == subject
            ),
            None,
        )

        if match:
            formatted_subject = (
                f"{match.get(config_data.DataframeHeaders_RU_ID, "-")} | {subject} | CS={similarity:.4f} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[2], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[1], "-")} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[3], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[4], "-")} | "
                f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[5], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[6], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[7], "-")} | "
                + f"{match.get(config_data.DataframeHeaders_RU_SUBJECTS[8], "-")}"
            )
        else:
            formatted_subject = f"- | {subject} | CS={similarity:.4f}"

        all_top_items.append(formatted_subject)

    subjects_sorted = sort_subjects(all_top_items)

    grouped_subjects = {}
    for subject in subjects_sorted.split(";"):
        subject_info = list(map(str.strip, subject.split("|")))

        for grade, mean_grade in zip(
            config_data.DataframeHeaders_COURSES_GRADES[::2],
            config_data.DataframeHeaders_COURSES_GRADES[1::2],
        ):
            if grade not in dropdown_courses_grades:
                subject_info.extend(["-", "-"])
                continue

            course_grades = df_courses_grades.filter(
                pl.col(config_data.DataframeHeaders_RU_ID) == int(subject_info[0])
            )[0]

            curr_grade = round_if_number(course_grades[grade][0])
            mean_curr_grade = (
                round_if_number(course_grades[mean_grade][0])
                if mean_grade in course_grades.columns
                else "-"
            )

            subject_info.extend([curr_grade, mean_curr_grade])

        edu_level_label, edu_level = determine_edu_level(subject_info)

        if edu_level not in grouped_subjects:
            grouped_subjects[edu_level] = []
        grouped_subjects[edu_level].append((subject_info, edu_level_label, edu_level))

    content = ""

    vacancy_skills = skills_extractor.key_skills_for_profession(message)

    skills_vacancy = "".join(
        [f"<span class='skill'>{skill}</span>" for skill in vacancy_skills]
    )

    content += (
        f"<div class='subject-info{"-static" if not config_data.AppSettings_QUALITY else ""}'>"
        "<div class='info'><div class='info-skills'><span class='label'>"
        + (
            config_data.HtmlContent_VACANCY_LABEL.format(
                "<span class='important'>"
                + config_data.HtmlContent_VACANCY_LABEL_CLICK
                + "</span>"
            )
            if config_data.AppSettings_QUALITY
            else config_data.HtmlContent_VACANCY_LABEL_STATIC
        )
        + "</span> <span class='value'>"
        + f"{skills_vacancy}</span></div></div></div>"
    )

    item = 1

    for edu_level, subjects in grouped_subjects.items():
        content += (
            f"<div class='edu-group'><span>{edu_level}</span><div class='subject-info'>"
        )

        content += "".join(
            "<div class='info'>"
            f"<div class='item'>{item}</div>"
            + generate_subject_info(subject_info, edu_level_label, edu_level)
            + generate_skills(subject_info[0], max_skill_words)
            + "</div>"
            for item, (subject_info, edu_level_label, edu_level) in enumerate(
                subjects, start=item
            )
        )

        item += len(subjects)

        content += "</div></div>"

    chat_history.append(ChatMessage(role="user", content=message))
    chat_history.append(ChatMessage(role="assistant", content=content))

    return (
        gr.Row(visible=not config_data.AppSettings_QUALITY),
        gr.Textbox(value=None, visible=not config_data.AppSettings_QUALITY),
        gr.Button(visible=not config_data.AppSettings_QUALITY),
        chat_history,
        gr.Column(visible=config_data.AppSettings_QUALITY),
        gr.Dropdown(
            visible=config_data.AppSettings_QUALITY,
            interactive=config_data.AppSettings_QUALITY,
        ),
        gr.HTML(visible=config_data.AppSettings_QUALITY),
        gr.Textbox(visible=config_data.AppSettings_QUALITY),
        gr.Column(visible=config_data.AppSettings_QUALITY),
        gr.Button(
            visible=config_data.AppSettings_QUALITY,
            interactive=config_data.AppSettings_QUALITY,
        ),
    )
