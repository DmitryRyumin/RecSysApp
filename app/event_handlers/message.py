"""
File: auth.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Event handler for Gradio app to change message.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app


def event_handler_message(message: str) -> gr.Button:
    message = message.strip()

    return gr.Button(interactive=bool(message))
