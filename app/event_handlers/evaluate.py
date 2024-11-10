"""
File: evaluate.py
Author: Dmitry Ryumin
Description: Event handler for Gradio app to evaluate.
License: MIT License
"""

import gradio as gr
from gradio import ChatMessage

# Importing necessary components for the Gradio app


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
        gr.Dropdown(choices=None, value=[], interactive=False, visible=False),
        gr.HTML(visible=False),
        gr.Textbox(visible=False),
        gr.Column(visible=False),
        gr.Button(visible=False, interactive=False),
    )
