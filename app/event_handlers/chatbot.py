"""
File: chatbot.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to chatbor.
License: MIT License
"""

import gradio as gr
from gradio import ChatMessage


def event_handler_chatbot_clear() -> tuple[
    gr.Row,
    gr.Textbox,
    gr.Button,
    list[ChatMessage],
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
        gr.Textbox(value=None, visible=True),
        gr.Button(visible=True),
        gr.Chatbot(
            value=None,
            type="messages",
        ),
        gr.Column(visible=False),
        gr.Dropdown(choices=None, value=[], interactive=False, visible=False),
        gr.Dropdown(choices=None, value=[], interactive=False, visible=False),
        gr.HTML(visible=False),
        gr.Textbox(visible=False),
        gr.Column(visible=False),
        gr.Button(visible=False, interactive=False),
    )
