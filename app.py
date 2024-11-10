"""
File: app.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Main application file.
             The file defines the Gradio interface, sets up the main blocks and tabs,
             and includes event handlers for various components.
License: MIT License
"""

import gradio as gr
import os
import threading
import signal
import sys

from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Importing necessary components for the Gradio app
from app.config import CONFIG_NAME, config_data, load_tab_creators
from app.event_handlers.event_handlers import setup_app_event_handlers
from app.header import HEADER
from app.port import is_port_in_use, free_ports
from app.server import run_server, stop_server_func
import app.tabs


gr.set_static_paths(
    paths=[
        config_data.Path_APP / config_data.StaticPaths_IMAGES,
        config_data.Path_APP / config_data.StaticPaths_FONTS,
    ]
)

JS_HEAD = f"<script>{Path(
    config_data.Path_APP / config_data.StaticPaths_JS / "head.js"
).read_text(encoding='utf-8')}</script>"


def signal_handler(sig, frame):
    stop_server_func()
    sys.exit(0)


def create_gradio_app() -> gr.Blocks:
    with gr.Blocks(
        title=config_data.AppSettings_TITLE,
        theme=gr.themes.Default(font=["HSESans"]),
        css_paths=config_data.AppSettings_CSS_PATH,
        head=JS_HEAD,
    ) as gradio_app:
        gr.HTML(HEADER)

        tab_instances = {}

        available_functions = {
            name: func
            for name, func in vars(app.tabs).items()
            if callable(func) and name.endswith("_tab")
        }

        tab_creators = load_tab_creators(CONFIG_NAME, available_functions)

        tab_show = lambda tab_name: not (
            config_data.AppSettings_QUALITY
            and tab_name in config_data.TabCreatorsHide_QUALITY
        )

        for tab_name, create_tab_function in tab_creators.items():
            with gr.Tab(
                tab_name,
                interactive=tab_show(tab_name),
                visible=tab_show(tab_name),
                render=tab_show(tab_name),
            ):
                tab_instances[tab_name] = create_tab_function()

        keys = list(tab_instances.keys())

        setup_app_event_handlers(
            *(tab_instances.get(keys[0]) + tab_instances.get(keys[1]))
        )

    return gradio_app


if __name__ == "__main__":
    ports_to_check = [
        config_data.AppSettings_PORT,
        (
            config_data.AppSettings_SERVER_PORT
            if config_data.AppSettings_QUALITY
            else None
        ),
    ]

    for port in filter(None, ports_to_check):
        if is_port_in_use(config_data.AppSettings_SERVER_NAME, port):
            free_ports(port)

    if config_data.AppSettings_QUALITY:
        signal.signal(signal.SIGINT, signal_handler)

        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

    try:
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
            server_name=config_data.AppSettings_SERVER_NAME,
            server_port=config_data.AppSettings_PORT,
        )
    except KeyboardInterrupt:
        pass
    finally:
        if config_data.AppSettings_QUALITY:
            stop_server_func()
            server_thread.join()
