"""
File: evaluate.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to evaluate.
License: MIT License
"""

import gradio as gr
from gradio import ChatMessage

# Importing necessary components for the Gradio app
from app.config import config_data
from app.html_components import ADD_RANGE


def event_handler_evaluate() -> tuple[
    list[ChatMessage],
    gr.Column,
    gr.Dropdown,
    gr.HTML,
    gr.Textbox,
    gr.Column,
    gr.Button,
]:
    return (
        gr.Chatbot(
            value=None,
            type="messages",
        ),
        gr.Column(visible=False),
        gr.Dropdown(choices=None, value=None, interactive=False, visible=False),
        gr.HTML(
            value=ADD_RANGE.format(
                config_data.HtmlContent_USEFULNESS_CURRENT,
                config_data.HtmlContent_DEMAND_CURRENT,
                config_data.HtmlContent_INTERFACE_CURRENT,
            ),
            visible=False,
        ),
        gr.Textbox(value=None, visible=False),
        gr.Column(visible=False),
        gr.Button(visible=False, interactive=False),
    )
