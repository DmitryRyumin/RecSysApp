"""
File: auth.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to change auth.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data
from app.components import html_message


def event_handler_auth(
    username: str, group_number: str, dropdown_role: str
) -> tuple[gr.Button, gr.HTML]:
    username = username.strip()
    group_number = group_number.strip()

    is_auth_valid = username and dropdown_role

    return (
        gr.Button(interactive=is_auth_valid),
        html_message(
            message=config_data.InformationMessages_NOTI_AUTH[
                1 if is_auth_valid else 0
            ],
            error=not is_auth_valid,
        ),
    )
