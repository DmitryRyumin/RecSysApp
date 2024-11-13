"""
File: tabs.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Gradio app tabs - Contains the definition of various tabs for the Gradio app interface.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.description import DESCRIPTION
from app.instruction import INSTRUCTION_TEXT
from app.description_steps import STEP_1, STEP_2, INSTRUCTION
from app.html_components import ADD_RANGE
from app.config import config_data
from app.requirements_app import read_requirements
from app.components import html_message


def app_tab():
    with gr.Row(
        visible=True,
        render=True,
        variant="default",
        elem_classes="account-container",
    ):
        gr.Markdown(value=DESCRIPTION)

        account = gr.Button(
            value=config_data.OtherMessages_ACCOUNT,
            interactive=False,
            scale=1,
            visible=False,
            elem_classes=["account", "hide"],
        )

    step_1 = gr.HTML(value=STEP_1)

    with gr.Row(
        visible=True,
        render=True,
        variant="default",
        elem_classes="user-container",
    ):
        userid = gr.Textbox(
            value=None,
            lines=1,
            max_lines=1,
            placeholder=None,
            label=None,
            info=None,
            show_label=False,
            container=False,
            scale=1,
            interactive=False,
            visible=False,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=None,
            elem_classes="user-id",
        )

        username = gr.Textbox(
            value=None,
            lines=1,
            max_lines=1,
            placeholder=config_data.OtherMessages_IMPORTANT,
            label=config_data.Labels_USERNAME,
            info=None,
            show_label=True,
            container=True,
            scale=1,
            interactive=True,
            visible=True,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=config_data.Settings_USER_MAX_LENGTH,
            elem_classes="user-info",
        )

        group_number = gr.Textbox(
            value=None,
            lines=1,
            max_lines=1,
            placeholder=None,
            label=config_data.Labels_GROUP_NUMBER,
            info=None,
            show_label=True,
            container=True,
            scale=1,
            interactive=True,
            visible=True,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=config_data.Settings_USER_MAX_LENGTH,
            elem_classes="user-info",
        )

        dropdown_role = gr.Dropdown(
            choices=config_data.Settings_DROPDOWN_ROLE,
            value=None,
            multiselect=False,
            allow_custom_value=False,
            label=config_data.Labels_USER_ROLE,
            info=None,
            show_label=True,
            interactive=True,
            visible=True,
            render=True,
            elem_classes="dropdown-user",
        )

    with gr.Row(
        visible=True,
        render=True,
        variant="default",
        elem_classes="auth-container",
    ) as auth_row:
        auth = gr.Button(
            value=config_data.OtherMessages_AUTH,
            interactive=False,
            scale=1,
            # icon=config_data.Path_APP / config_data.StaticPaths_IMAGES / "auth.ico",
            visible=True,
            elem_classes="auth",
        )

    noti_auth = html_message(
        message=config_data.InformationMessages_NOTI_AUTH[0],
        error=True,
        visible=True,
    )

    with gr.Column(
        visible=False,
        render=True,
        variant="default",
        elem_classes="user-instruction",
    ) as instruction_column:
        instruction = gr.HTML(
            value=INSTRUCTION, visible=False, elem_classes="instruction"
        )

        instruction_text = gr.HTML(
            value=INSTRUCTION_TEXT, visible=False, elem_classes="instruction_text"
        )

        start_evaluate = gr.Button(
            value=config_data.OtherMessages_START_EVALUATE,
            interactive=False,
            scale=1,
            # icon=config_data.Path_APP / config_data.StaticPaths_IMAGES / "ok.ico",
            visible=False,
            elem_classes="start_evaluate",
        )

    step_2 = gr.HTML(value=STEP_2, visible=False, elem_classes="step-2")

    with gr.Column(
        visible=False,
        render=True,
        variant="default",
        elem_classes="chatbot-container",
    ) as chatbot_column:
        chatbot = gr.Chatbot(
            type="messages",
            label=config_data.Labels_CHATBOT,
            autoscroll=False,
            visible=False,
            render=True,
            show_copy_button=True,
            avatar_images=(
                config_data.Path_APP / config_data.StaticPaths_IMAGES / "user.svg",
                config_data.Path_APP / config_data.StaticPaths_IMAGES / "HSE.svg",
            ),
            elem_classes="chatbot",
        )

        chatbot_timer = gr.Textbox(
            value=None,
            lines=1,
            max_lines=1,
            placeholder=None,
            label=None,
            info=None,
            show_label=False,
            container=False,
            scale=1,
            interactive=False,
            visible=False,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=None,
            elem_classes="chatbot-timer",
        )

        with gr.Row(
            visible=False,
            render=True,
            variant="default",
            elem_classes="message-container",
        ) as message_row:
            message = gr.Textbox(
                value=None,
                lines=1,
                max_lines=20,
                placeholder=config_data.OtherMessages_JOB_DESC,
                label=None,
                info=None,
                show_label=False,
                container=False,
                scale=7,
                interactive=True,
                visible=False,
                autofocus=False,
                autoscroll=True,
                render=True,
                type="text",
                show_copy_button=True,
                max_length=None,
            )

            send_message = gr.Button(
                value="",
                interactive=False,
                scale=1,
                icon=config_data.Path_APP
                / config_data.StaticPaths_IMAGES
                / "btn_message.svg",
                visible=False,
                elem_classes="send_message",
            )

    with gr.Column(
        visible=False,
        render=True,
        variant="default",
        elem_classes="add_evals-container",
    ) as add_evals_column:
        add_vacancy_skills = gr.Dropdown(
            choices=None,
            value=None,
            multiselect=True,
            allow_custom_value=True,
            label=config_data.Labels_ADD_VACANCY_SKILLS,
            info=None,
            show_label=True,
            interactive=False,
            visible=False,
            render=True,
            elem_classes="dropdown-add-vacancy-skills",
        )

        add_range = gr.HTML(
            value=ADD_RANGE.format(
                config_data.HtmlContent_USEFULNESS_CURRENT,
                config_data.HtmlContent_DEMAND_CURRENT,
                config_data.HtmlContent_INTERFACE_CURRENT,
            ),
            visible=False,
            elem_classes="add-range",
        )

        feedback = gr.Textbox(
            value=None,
            lines=3,
            max_lines=20,
            placeholder=None,
            label=config_data.Labels_FEEDBACK,
            info=None,
            show_label=True,
            container=True,
            scale=7,
            interactive=True,
            visible=False,
            autofocus=False,
            autoscroll=True,
            render=True,
            type="text",
            show_copy_button=False,
            max_length=None,
            elem_classes="feedback",
        )

    add_subjects_skills = gr.Dropdown(
        choices=None,
        value=None,
        multiselect=True,
        allow_custom_value=True,
        label=config_data.Labels_ADD_SUBJECTS_SKILLS,
        info=None,
        show_label=True,
        interactive=False,
        visible=False,
        render=True,
        elem_classes="dropdown-add-subjects-skills",
    )

    with gr.Column(
        visible=False,
        render=True,
        variant="default",
        elem_classes="evaluate-container",
    ) as evaluate_column:
        send_evaluate = gr.Button(
            value=config_data.OtherMessages_EVALUATE,
            interactive=False,
            scale=1,
            # icon=config_data.Path_APP / config_data.StaticPaths_IMAGES / "evaluate.ico",
            visible=False,
            elem_classes="send_evaluate",
        )

    return (
        account,
        step_1,
        userid,
        username,
        group_number,
        dropdown_role,
        auth_row,
        auth,
        noti_auth,
        instruction_column,
        instruction,
        instruction_text,
        start_evaluate,
        step_2,
        chatbot_column,
        chatbot,
        chatbot_timer,
        message_row,
        message,
        send_message,
        add_evals_column,
        add_vacancy_skills,
        add_subjects_skills,
        add_range,
        feedback,
        evaluate_column,
        send_evaluate,
    )


def settings_app_tab():
    with gr.Column(
        visible=True,
        render=True,
        variant="default",
        elem_classes="settings-container",
    ):
        type_recommendation = (
            gr.Radio(
                choices=config_data.Settings_TYPE_RECOMMENDATION,
                value=config_data.Settings_TYPE_RECOMMENDATION[0],
                label=config_data.Labels_TYPE_RECOMMENDATION,
                info=None,
                show_label=True,
                container=True,
                interactive=True,
                visible=True,
                render=True,
                elem_classes="settings-type-recommendation",
            ),
        )

        with gr.Row(
            visible=True,
            render=True,
            variant="default",
            elem_classes="row-1-container",
        ):
            top_subjects = gr.Number(
                value=(
                    config_data.Settings_TOP_SUBJECTS
                    if not config_data.AppSettings_QUALITY
                    else config_data.Settings_TOP_SUBJECTS_QUALITY
                ),
                label=config_data.Labels_TOP_SUBJECTS,
                info=config_data.InformationMessages_FROM_TO.format(
                    config_data.Settings_TOP_SUBJECTS_RANGE[0],
                    config_data.Settings_TOP_SUBJECTS_RANGE[1],
                ),
                show_label=True,
                container=True,
                scale=1,
                interactive=True,
                visible=True,
                render=True,
                minimum=config_data.Settings_TOP_SUBJECTS_RANGE[0],
                maximum=config_data.Settings_TOP_SUBJECTS_RANGE[1],
                step=1,
                elem_classes="settings-item",
            )

            max_skill_words = gr.Number(
                value=config_data.Settings_MAX_SKILL_WORDS,
                label=config_data.Labels_MAX_SKILL_WORDS,
                info=config_data.InformationMessages_FROM_TO.format(
                    config_data.Settings_MAX_SKILL_WORDS_RANGE[0],
                    config_data.Settings_MAX_SKILL_WORDS_RANGE[1],
                ),
                show_label=True,
                container=True,
                scale=1,
                interactive=True,
                visible=True,
                render=True,
                minimum=config_data.Settings_MAX_SKILL_WORDS_RANGE[0],
                maximum=config_data.Settings_MAX_SKILL_WORDS_RANGE[1],
                step=1,
                elem_classes="settings-item",
            )

            dropdown_models = gr.Dropdown(
                choices=config_data.Models_SBERT,
                value=config_data.Models_SBERT[0],
                multiselect=False,
                allow_custom_value=False,
                label=config_data.Labels_MODEL,
                info=config_data.InformationMessages_MODEL,
                show_label=True,
                interactive=True,
                visible=True,
                render=True,
                elem_classes="dropdown-models",
            )
        with gr.Row(
            visible=True,
            render=True,
            variant="default",
            elem_classes="row-2-container",
        ):
            dropdown_courses_grades = gr.Dropdown(
                choices=config_data.DataframeHeaders_COURSES_GRADES[::2],
                value=config_data.DataframeHeaders_COURSES_GRADES[0],
                multiselect=True,
                allow_custom_value=False,
                label=config_data.Labels_COURSES_GRADES,
                info=config_data.InformationMessages_COURSES_GRADES,
                show_label=True,
                interactive=True,
                visible=True,
                render=True,
                elem_classes="dropdown-courses-grades",
            )

    return (
        type_recommendation,
        top_subjects,
        max_skill_words,
        dropdown_models,
        dropdown_courses_grades,
    )


# def about_app_tab():
#     pass


# def about_authors_tab():
#     pass


def requirements_app_tab():
    reqs = read_requirements()

    return gr.Dataframe(
        headers=reqs.columns,
        value=reqs,
        datatype=["markdown"] * len(reqs.columns),
        visible=True,
        elem_classes="requirements-dataframe",
        type="polars",
    )
