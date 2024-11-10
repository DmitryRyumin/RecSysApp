"""
File: config.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Configuration module for handling settings.
License: MIT License
"""

import tomllib
from pathlib import Path
from collections.abc import Callable
from types import SimpleNamespace

CONFIG_NAME = "config.toml"


def flatten_dict(prefix: str, d: dict) -> dict:
    result = {}

    for k, v in d.items():
        result.update(
            flatten_dict(f"{prefix}{k}_", v)
            if isinstance(v, dict)
            else {f"{prefix}{k}": v}
        )

    return result


def load_tab_creators(
    file_path: str, available_functions: dict[str, Callable]
) -> dict[str, Callable]:
    with open(file_path, "rb") as f:
        config = tomllib.load(f)

    tab_creators_data = config.get("TabCreators", {})

    return {key: available_functions[value] for key, value in tab_creators_data.items()}


def load_config(file_path: str) -> SimpleNamespace:
    with open(file_path, "rb") as f:
        config = tomllib.load(f)

    config_data = flatten_dict("", config)

    config_namespace = SimpleNamespace(**config_data)

    setattr(config_namespace, "Path_APP", Path(__file__).parent.parent.resolve())

    return config_namespace


config_data = load_config(CONFIG_NAME)
