"""
File: components.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Utility functions for creating Gradio components.
License: MIT License
"""

import gradio as gr

# Importing necessary components for the Gradio app


def html_message(
    message: str = "", error: bool = True, visible: bool = True
) -> gr.HTML:
    css_class = "noti_err" if error else "noti_true"

    return gr.HTML(value=f"<h3 class='{css_class}'>{message}</h3>", visible=visible)
