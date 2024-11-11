"""
File: login.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to login.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data
from app.components import html_message
from app.data_utils import generate_user_id


def event_handler_login(username: str, group_number: str, dropdown_role: str) -> tuple[
    gr.Button,
    gr.HTML,
    gr.Textbox,
    gr.Textbox,
    gr.Textbox,
    gr.Dropdown,
    gr.Row,
    gr.Button,
    gr.HTML,
    gr.Column,
    gr.HTML,
    gr.HTML,
    gr.Button,
    gr.HTML,
    gr.Row,
    gr.Column,
    gr.Chatbot,
    gr.Textbox,
    gr.Button,
]:
    username = username.strip()
    group_number = group_number.strip()

    is_auth_valid = username and dropdown_role

    return (
        gr.Button(
            value=(username),
            interactive=is_auth_valid,
            visible=is_auth_valid,
            elem_classes=[
                "account",
                "hide" if not is_auth_valid else "show",
            ],
        ),
        gr.HTML(visible=not is_auth_valid),
        gr.Textbox(value=generate_user_id() if is_auth_valid else None),
        gr.Textbox(
            value=username, interactive=not is_auth_valid, visible=not is_auth_valid
        ),
        gr.Textbox(
            value=group_number, interactive=not is_auth_valid, visible=not is_auth_valid
        ),
        gr.Dropdown(interactive=not is_auth_valid, visible=not is_auth_valid),
        gr.Row(visible=not is_auth_valid),
        gr.Button(
            interactive=not is_auth_valid,
            visible=not is_auth_valid,
            elem_classes=[
                "auth",
                "hide" if is_auth_valid else None,
            ],
        ),
        html_message(
            message=config_data.InformationMessages_NOTI_AUTH[
                1 if is_auth_valid else 0
            ],
            error=not is_auth_valid,
            visible=not is_auth_valid,
        ),
        gr.Column(visible=is_auth_valid and config_data.AppSettings_QUALITY),
        gr.HTML(visible=is_auth_valid and config_data.AppSettings_QUALITY),
        gr.HTML(visible=is_auth_valid and config_data.AppSettings_QUALITY),
        gr.Button(
            interactive=is_auth_valid and config_data.AppSettings_QUALITY,
            visible=is_auth_valid and config_data.AppSettings_QUALITY,
        ),
        gr.HTML(visible=is_auth_valid and not config_data.AppSettings_QUALITY),
        gr.Row(visible=is_auth_valid and not config_data.AppSettings_QUALITY),
        gr.Column(visible=is_auth_valid and not config_data.AppSettings_QUALITY),
        gr.Chatbot(
            type="messages",
            visible=is_auth_valid and not config_data.AppSettings_QUALITY,
        ),
        gr.Textbox(
            value=None, visible=is_auth_valid and not config_data.AppSettings_QUALITY
        ),
        gr.Button(visible=is_auth_valid and not config_data.AppSettings_QUALITY),
    )
