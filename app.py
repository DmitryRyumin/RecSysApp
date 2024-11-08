"""
File: app.py
Author: Dmitry Ryumin
Description: Main application file.
             The file defines the Gradio interface, sets up the main blocks and tabs,
             and includes event handlers for various components.
License: MIT License
"""

import gradio as gr
import os

from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Importing necessary components for the Gradio app
from app.config import CONFIG_NAME, config_data, load_tab_creators
from app.event_handlers.event_handlers import setup_app_event_handlers
import app.tabs
from app.header import HEADER

gr.set_static_paths(
    paths=[
        config_data.Path_APP / config_data.StaticPaths_IMAGES,
        config_data.Path_APP / config_data.StaticPaths_FONTS,
    ]
)

JS_HEAD = f"<script>{Path(
    config_data.Path_APP / config_data.StaticPaths_JS / "head.js"
).read_text(encoding='utf-8')}</script>"


def create_gradio_app() -> gr.Blocks:
    with gr.Blocks(
        title=config_data.AppSettings_TITLE,
        theme=gr.themes.Default(font=["HSESans"]),
        css_paths=config_data.AppSettings_CSS_PATH,
        head=JS_HEAD,
    ) as gradio_app:
        gr.HTML(HEADER)

        tab_results = {}

        available_functions = {
            attr: getattr(app.tabs, attr)
            for attr in dir(app.tabs)
            if callable(getattr(app.tabs, attr)) and attr.endswith("_tab")
        }

        tab_creators = load_tab_creators(CONFIG_NAME, available_functions)

        for tab_name, create_tab_function in tab_creators.items():
            with gr.Tab(tab_name):
                app_instance = create_tab_function()
                tab_results[tab_name] = app_instance

        keys = list(tab_results.keys())

        setup_app_event_handlers(*(tab_results[keys[0]] + tab_results[keys[1]]))

    return gradio_app


if __name__ == "__main__":
    create_gradio_app().queue(api_open=False).launch(
        favicon_path=config_data.Path_APP
        / config_data.StaticPaths_IMAGES
        / "favicon.ico",
        share=False,
        allowed_paths=[
            "fonts/HSE_Sans/HSESans-Regular.otf",
            "fonts/HSE_Sans/HSESans-Bold.otf",
            "fonts/HSE_Sans/HSESans-Italic.otf",
            "fonts/HSE_Sans/HSESans-SemiBold.otf",
            "fonts/HSE_Sans/HSESans-Black.otf",
            "fonts/HSE_Sans/HSESans-Thin.otf",
        ],
    )
