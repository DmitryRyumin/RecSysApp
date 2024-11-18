"""
File: generate_response.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to generate response.
License: MIT License
"""

import re
import random
import torch
import polars as pl
import gradio as gr
from gradio import ChatMessage
from datetime import datetime, timezone

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
    sort_vacancies,
    round_if_number,
    format_grade,
    generate_user_id,
    create_numbered_list,
)
from app.dev import Dev


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


def generate_item_info(
    item_info: list[str], edu_level_label: str, edu_level: str
) -> str:
    number_education_block = (
        create_html_block(
            (
                config_data.HtmlContent_NUMBERS_EDUCATION
                if "-" in item_info[10]
                else config_data.HtmlContent_NUMBER_EDUCATION
            ),
            item_info[10],
        )
        if item_info[10] != "-"
        else "<div class='info-number-education-error'><span class='label'>"
        + config_data.InformationMessages_LEVEL_NOT_DEFINED
        + "</span></div>"
    )

    return "".join(
        [
            create_html_range(
                config_data.HtmlContent_SUBJECT_RELEVANCE,
                item_info[0],
                "subject_relevance",
            ),
            create_html_block(config_data.HtmlContent_SUBJECT_LABEL, item_info[1]),
            create_html_block(config_data.HtmlContent_ID_SUBJECT_LABEL, item_info[0]),
            create_html_block(config_data.HtmlContent_DEPARTMENT_LABEL, item_info[5]),
            create_html_block(config_data.HtmlContent_FACULTY_LABEL, item_info[4]),
            create_html_block(config_data.HtmlContent_CAMPUS_LABEL, item_info[3]),
            create_html_block(edu_level_label, edu_level),
            number_education_block,
            create_html_block(config_data.HtmlContent_AUDIENCE_LABEL, item_info[8]),
            create_html_block(config_data.HtmlContent_FORMAT_LABEL, item_info[9]),
            generate_courses_grades(item_info),
        ]
    )


def generate_subject_skills(item_id: str, max_skill_words: int) -> str:
    try:
        if not config_data.AppSettings_DEV:
            item_skills = (
                df_puds_skills.filter(
                    pl.col(config_data.DataframeHeaders_RU_ID) == int(item_id)
                )[0]["LLM_Skills"][0]
                .strip()
                .split(";")
            )

            skills = [
                re.sub(r"[.,;:\s]+$", "", skill.strip()).capitalize()
                for skill in item_skills
                if len(skill.split()) <= max_skill_words and skill.strip()
            ]
        else:
            skills = (
                create_numbered_list(Dev.SUBJECT_SKILLS) if random.randint(0, 1) else []
            )

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
            + config_data.InformationMessages_SUBJECT_SKILLS_NOT_DEFINED
            + "</span></div>"
        )


def generate_vacancy_skills(skills: str, max_skill_words: int) -> str:
    try:
        if not config_data.AppSettings_DEV:
            skills = [
                re.sub(r"[.,;:\s]+$", "", skill.strip())
                for skill in skills.split(",")
                if len(skill.split()) <= max_skill_words
                and skill.strip()
                and skill.strip().lower() != "none"
            ]
        else:
            skills = (
                create_numbered_list(Dev.SUBJECT_SKILLS) if random.randint(0, 1) else []
            )

        if not skills:
            raise ValueError

        skills_content = "".join(
            [f"<span class='skill'>{skill}</span>" for skill in skills]
        )
        return (
            f"<div class='info-skills{"-static" if not config_data.AppSettings_QUALITY else ""}'><span class='label'>"
            + config_data.HtmlContent_VACANCY_SKILLS_LABEL_STATIC
            + "</span> <span class='value'>"
            + f"{skills_content}</span></div>"
        )
    except Exception:
        return (
            "<div class='info-skills-error'><span class='label'>"
            + config_data.InformationMessages_VACANCY_SKILLS_NOT_DEFINED
            + "</span></div>"
        )


def get_default_ui_response(chat_history: list[ChatMessage]) -> tuple[
    gr.Row,
    gr.Textbox,
    gr.Button,
    list[ChatMessage],
    gr.Textbox,
    gr.Column,
    gr.Dropdown,
    gr.Dropdown,
    gr.HTML,
    gr.Textbox,
    gr.Column,
    gr.Button,
]:
    return (
        gr.Row(visible=True),
        gr.Textbox(value=None),
        gr.Button(visible=True),
        chat_history,
        gr.Textbox(value=None, visible=False),
        gr.Column(visible=False),
        gr.Dropdown(interactive=False, visible=False),
        gr.Dropdown(interactive=False, visible=False),
        gr.HTML(visible=False),
        gr.Textbox(value=None, visible=False),
        gr.Column(visible=False),
        gr.Button(visible=False, interactive=False),
    )


def event_handler_generate_response(
    message: str,
    chat_history: list[ChatMessage],
    type_recommendation: str,
    top_items: int,
    max_skill_words: int,
    dropdown_courses_grades: list[str],
) -> tuple[
    gr.Row,
    gr.Textbox,
    gr.Button,
    gr.Textbox,
    list[ChatMessage],
    gr.Textbox,
    gr.Column,
    gr.Dropdown,
    gr.Dropdown,
    gr.HTML,
    gr.Textbox,
    gr.Column,
    gr.Button,
]:
    message = message.strip()

    if not message:
        return get_default_ui_response(chat_history)

    if config_data.AppSettings_QUALITY:
        type_recommendation, top_items, max_skill_words, dropdown_courses_grades = (
            config_data.Settings_TYPE_RECOMMENDATION[0],
            config_data.Settings_TOP_ITEMS_QUALITY,
            config_data.Settings_MAX_SKILL_WORDS,
            config_data.DataframeHeaders_COURSES_GRADES[0:1],
        )

    if not config_data.AppSettings_DEV:
        embedding = get_embeddings(message, model_manager_sbert.get_current_model())

        with torch.no_grad():
            similarities = (
                cosine_similarity(embedding, model_manager_sbert.state.embeddings)
                .cpu()
                .tolist()
            )
            similarities = [
                (name, sim)
                for name, sim in zip(
                    model_manager_sbert.state.names["names"], similarities
                )
            ]

        unique_items = filter_unique_items(
            sorted(similarities, key=lambda x: x[1], reverse=True), top_items
        )

        all_top_items = []

        for item, similarity in unique_items:
            if type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[0]:
                match = next(
                    (
                        itm
                        for itm in model_manager_sbert.get_puds_data()
                        if itm.get(config_data.DataframeHeaders_RU_SUBJECTS[0]) == item
                    ),
                    None,
                )

                if match:
                    formatted_item = (
                        f"{match.get(config_data.DataframeHeaders_RU_ID, "-")} | {item} | CS={similarity:.4f} | "
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
                    formatted_item = f"- | {item} | CS={similarity:.4f}"
            elif type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[1]:
                match = next(
                    (
                        itm
                        for itm in model_manager_sbert.get_vacancies_data()
                        if itm.get(config_data.DataframeHeaders_VACANCIES[1]) == item
                    ),
                    None,
                )

                if match:
                    formatted_item = (
                        f"{item} | CS={similarity:.4f} | "
                        f"{match.get(config_data.DataframeHeaders_VACANCIES[3], "-")}"
                    )
                else:
                    formatted_item = f"{item} | CS={similarity:.4f}"

            all_top_items.append(formatted_item)

        if type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[0]:
            items_sorted = sort_subjects(all_top_items)

            grouped_items = {}
            for item in items_sorted.split(";"):
                item_info = list(map(str.strip, item.split("|")))

                for grade, mean_grade in zip(
                    config_data.DataframeHeaders_COURSES_GRADES[::2],
                    config_data.DataframeHeaders_COURSES_GRADES[1::2],
                ):
                    if grade not in dropdown_courses_grades:
                        item_info.extend(["-", "-"])
                        continue

                    course_grades = df_courses_grades.filter(
                        pl.col(config_data.DataframeHeaders_RU_ID) == int(item_info[0])
                    )[0]

                    curr_grade = round_if_number(course_grades[grade][0])
                    mean_curr_grade = (
                        round_if_number(course_grades[mean_grade][0])
                        if mean_grade in course_grades.columns
                        else "-"
                    )

                    item_info.extend([curr_grade, mean_curr_grade])

                edu_level_label, edu_level = determine_edu_level(item_info)

                if edu_level not in grouped_items:
                    grouped_items[edu_level] = []
                grouped_items[edu_level].append((item_info, edu_level_label, edu_level))
        elif type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[1]:
            items_sorted = sort_vacancies(all_top_items)

    content = ""

    if type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[0]:
        if not config_data.AppSettings_DEV:
            vacancy_skills = skills_extractor.key_skills_for_profession(message)
        else:
            vacancy_skills = create_numbered_list(Dev.VACANCY_SKILLS)

        skills_vacancy = "".join(
            [f"<span class='skill'>{skill}</span>" for skill in vacancy_skills]
        )

        content += (
            f"<div class='subject-info{"-static" if not config_data.AppSettings_QUALITY else ""}'>"
            "<div class='info'><div class='info-skills'><span class='label'>"
            + (
                config_data.HtmlContent_VACANCY_SKILLS_LABEL.format(
                    "<span class='important'>"
                    + config_data.HtmlContent_VACANCY_SKILLS_LABEL_CLICK
                    + "</span>"
                )
                if config_data.AppSettings_QUALITY
                else config_data.HtmlContent_VACANCY_SKILLS_LABEL_STATIC
            )
            + "</span> <span class='value'>"
            + f"{skills_vacancy}</span></div></div></div>"
        )

        item = 1

        if config_data.AppSettings_DEV:
            grouped_items = Dev.GROUPED_ITEMS

        for edu_level, items in grouped_items.items():
            content += f"<div class='edu-group'><span>{edu_level}</span><div class='subject-info'>"

            content += "".join(
                "<div class='info'>"
                f"<div class='item'>{item}</div>"
                + generate_item_info(item_info, edu_level_label, edu_level)
                + generate_subject_skills(item_info[0], max_skill_words)
                + "</div>"
                for item, (item_info, edu_level_label, edu_level) in enumerate(
                    items, start=item
                )
            )

            item += len(items)

            content += "</div></div>"
    elif type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[1]:
        if config_data.AppSettings_DEV:
            items_sorted = Dev.ITEMS_SORTED

        content += (
            "<div class='vacancy-info-static'>"
            + "".join(
                "<div class='info'>"
                + f"<div class='item'>{i}</div>"
                + create_html_block(
                    config_data.HtmlContent_VACANCY_LABEL, info.split("|")[0].strip()
                )
                + generate_vacancy_skills(info.split("|")[2].strip(), max_skill_words)
                + "</div>"
                for i, info in enumerate(
                    map(str.strip, items_sorted.split(";")), start=1
                )
            )
            + "</div>"
        )

    chat_history.append(ChatMessage(role="user", content=message))
    chat_history.append(ChatMessage(role="assistant", content=content))

    return (
        gr.Row(visible=not config_data.AppSettings_QUALITY),
        gr.Textbox(value=None, visible=not config_data.AppSettings_QUALITY),
        gr.Button(visible=not config_data.AppSettings_QUALITY),
        gr.Textbox(value=generate_user_id(), visible=False),
        chat_history,
        gr.Textbox(value=datetime.now(timezone.utc).timestamp(), visible=False),
        gr.Column(visible=config_data.AppSettings_QUALITY),
        gr.Dropdown(
            visible=config_data.AppSettings_QUALITY,
            interactive=config_data.AppSettings_QUALITY,
        ),
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
