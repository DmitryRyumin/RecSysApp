"""
File: instruction.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to instruction.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app
from app.config import config_data


def event_handler_instruction() -> tuple[
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
    return (
        gr.Column(visible=not config_data.AppSettings_QUALITY),
        gr.HTML(visible=not config_data.AppSettings_QUALITY),
        gr.HTML(visible=not config_data.AppSettings_QUALITY),
        gr.Button(
            interactive=not config_data.AppSettings_QUALITY,
            visible=not config_data.AppSettings_QUALITY,
        ),
        gr.HTML(visible=config_data.AppSettings_QUALITY),
        gr.Row(visible=config_data.AppSettings_QUALITY),
        gr.Column(visible=config_data.AppSettings_QUALITY),
        gr.Chatbot(
            type="messages",
            visible=config_data.AppSettings_QUALITY,
        ),
        gr.Textbox(value=None, visible=config_data.AppSettings_QUALITY),
        gr.Button(visible=config_data.AppSettings_QUALITY),
    )
