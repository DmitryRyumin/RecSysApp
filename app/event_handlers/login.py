"""
File: login.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to login.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data
from app.components import html_message


def event_handler_login(surname: str, username: str, dropdown_user: str) -> tuple[
    gr.Textbox,
    gr.Textbox,
    gr.Dropdown,
    gr.Button,
    gr.HTML,
    gr.HTML,
    gr.Row,
    gr.Column,
    gr.Chatbot,
    gr.Textbox,
    gr.Button,
]:
    surname = surname.strip()
    username = username.strip()

    is_auth_valid = surname and username and dropdown_user

    return (
        gr.Textbox(value=surname, interactive=not is_auth_valid),
        gr.Textbox(value=username, interactive=not is_auth_valid),
        gr.Dropdown(interactive=not is_auth_valid),
        gr.Button(
            value=config_data.OtherMessages_AUTH,
            interactive=not is_auth_valid,
            scale=1,
            # icon=config_data.Path_APP / config_data.StaticPaths_IMAGES / "auth.ico",
            visible=True,
            elem_classes="auth",
        ),
        html_message(
            message=config_data.InformationMessages_NOTI_AUTH[
                1 if is_auth_valid else 0
            ],
            error=not is_auth_valid,
            visible=not is_auth_valid,
        ),
        gr.HTML(visible=is_auth_valid),
        gr.Row(visible=is_auth_valid),
        gr.Column(visible=is_auth_valid),
        gr.Chatbot(type="messages", visible=is_auth_valid),
        gr.Textbox(value=None, visible=is_auth_valid),
        gr.Button(visible=is_auth_valid),
    )
