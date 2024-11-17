"""
File: settings.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to settings.
License: MIT License
"""

import gradio as gr
from gradio import ChatMessage

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_init import model_manager_sbert


def event_handler_type_recommendation(
    message: str, type_recommendation: str
) -> tuple[gr.Number, gr.Dropdown, gr.Row, gr.Dropdown, list[ChatMessage], gr.Button]:
    model_manager_sbert.change_model(config_data.Models_SBERT[0], type_recommendation)

    gr.Info(
        message=config_data.AppInfo_TYPE_RECOMMENDATION.format(type_recommendation),
        duration=config_data.AppInfo_DURATION,
        title=config_data.AppInfo_TITLE,
    )

    is_subjects = type_recommendation == config_data.Settings_TYPE_RECOMMENDATION[0]

    top_label = (
        config_data.Labels_TOP_SUBJECTS
        if is_subjects
        else config_data.Labels_TOP_VACANCIES
    )
    dropdown_label = (
        config_data.Labels_MODEL_SUBJECTS
        if is_subjects
        else config_data.Labels_MODEL_VACANCIES
    )
    dropdown_choices = (
        config_data.Models_SBERT if is_subjects else config_data.Models_SBERT[0:1]
    )
    chatbot_label = (
        config_data.Labels_CHATBOT_SUBJECTS
        if is_subjects
        else config_data.Labels_CHATBOT_VACANCIES
    )

    return (
        gr.Number(label=top_label),
        gr.Dropdown(
            choices=dropdown_choices,
            value=config_data.Models_SBERT[0],
            label=dropdown_label,
            interactive=is_subjects,
        ),
        gr.Row(visible=is_subjects),
        gr.Dropdown(visible=is_subjects),
        gr.Chatbot(
            label=chatbot_label,
            type="messages",
        ),
        gr.Button(interactive=bool(message.strip())),
    )


def event_handler_dropdown_models(
    message: str, type_recommendation: str, dropdown_models: str
) -> gr.Button:
    model_manager_sbert.change_model(dropdown_models, type_recommendation)

    gr.Info(
        message=config_data.AppInfo_MODEL.format(dropdown_models),
        duration=config_data.AppInfo_DURATION,
        title=config_data.AppInfo_TITLE,
    )

    message = message.strip()

    return gr.Button(interactive=bool(message))
