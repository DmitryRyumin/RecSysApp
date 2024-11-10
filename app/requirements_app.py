"""
File: requirements_app.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Project requirements for the Gradio app.
License: MIT License
"""

import polars as pl

# Importing necessary components for the Gradio app
from app.config import config_data


def read_requirements(file_path="requirements.txt"):
    with open(file_path, "r") as file:
        lines = file.readlines()

    data = []

    pypi = (
        lambda x: f"<a href='https://pypi.org/project/{x}' target='_blank'>"
        + f"<img src='https://img.shields.io/pypi/v/{x}' alt='PyPI' /></a>"
    )

    data = [
        {
            config_data.Requirements_LIBRARY: split_line[0],
            config_data.Requirements_RECOMMENDED_VERSION: split_line[1],
            config_data.Requirements_CURRENT_VERSION: pypi(split_line[0]),
        }
        for line in lines
        if (split_line := line.strip().split("==")) and len(split_line) == 2
    ]

    df = pl.DataFrame(data)

    return df
