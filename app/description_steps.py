"""
File: description_steps.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Project steps description for the Gradio app.
License: MIT License
"""

# Importing necessary components for the Gradio app
from app.config import config_data

STEPS_TEMPLATE = """\
<h2 align="center">{text}</h2>
"""

STEP_1 = STEPS_TEMPLATE.format(text=config_data.InformationMessages_STEP_1)

STEP_2 = STEPS_TEMPLATE.format(text=config_data.InformationMessages_STEP_2)
