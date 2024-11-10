"""
File: settings.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to settings.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_init import model_manager_sbert


def event_handler_dropdown_models(message: str, dropdown_models: str) -> gr.Button:
    model_manager_sbert.change_model(dropdown_models)

    gr.Info(
        message=config_data.AppInfo_MODEL.format(dropdown_models),
        duration=config_data.AppInfo_DURATION,
        title=config_data.AppInfo_TITLE,
    )

    message = message.strip()

    return gr.Button(interactive=bool(message))
