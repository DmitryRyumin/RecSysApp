"""
File: description.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Project description for the Gradio app.
License: MIT License
"""

# Importing necessary components for the Gradio app
from app.config import config_data

DESCRIPTION = f"""\
# Рекомендательная система

<div class="app-flex-container">
    <img src="https://img.shields.io/badge/version-v{config_data.AppSettings_APP_VERSION}-stable" alt="Версия">
</div>
"""
