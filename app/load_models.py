"""
File: load_models.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Classes for loading models and updating embeddings.
License: MIT License
"""

import torch
import polars as pl
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Optional

# Importing necessary components for the Gradio app
from app.gpu_init import device
from app.config import config_data
from app.data_utils import load_puds_data, load_vacancies_data, extract_embeddings


@dataclass
class ModelState:
    current_model: Optional[SentenceTransformer] = None
    embeddings: Optional[torch.Tensor] = field(default_factory=lambda: torch.empty(0))
    names: Optional[pl.DataFrame] = field(default_factory=pl.DataFrame)


@dataclass
class BaseModelManager:
    _puds_data: Optional[dict] = field(init=False, default=None)
    _vacancies_data: Optional[dict] = field(init=False, default=None)
    state: ModelState = field(default_factory=ModelState)

    def __post_init__(self):
        self._load_puds_data_once()
        self._load_vacancies_data_once()

    @classmethod
    def _load_puds_data_once(cls):
        if cls._puds_data is None and not config_data.AppSettings_DEV:
            df_puds_cleaned, _ = load_puds_data(
                path=config_data.Path_APP / config_data.StaticPaths_PUDS,
                year=config_data.DataframeHeaders_SUBJECTS_YEAR,
                drop_duplicates=True,
                subset=config_data.DataframeHeaders_RU_SUBJECTS[:2],
                drop_columns=None,
                full_info_cols=config_data.DataframeHeaders_SUBJECTS_FULL,
            )
            cls._puds_data = df_puds_cleaned.to_dicts()

    @classmethod
    def _load_vacancies_data_once(cls):
        if cls._vacancies_data is None and not config_data.AppSettings_DEV:
            df_vacancies_cleaned, _ = load_vacancies_data(
                path=config_data.Path_APP / config_data.StaticPaths_VACANCIES,
                drop_duplicates=False,
                subset=config_data.DataframeHeaders_VACANCIES[1:],
                drop_columns=config_data.DataframeHeaders_VACANCIES[0:1],
                full_info_cols=config_data.DataframeHeaders_VACANCIES[1:],
            )
            cls._vacancies_data = df_vacancies_cleaned.to_dicts()

    def get_puds_data(self) -> dict:
        if self._puds_data is None:
            return {}
        return self._puds_data

    def get_vacancies_data(self) -> dict:
        if self._vacancies_data is None:
            return {}
        return self._vacancies_data


@dataclass
class SbertModelManager(BaseModelManager):
    _loaded_models: dict = field(default_factory=dict, init=False)
    model_name: Optional[str] = None

    def load_model(self, model_name: str) -> SentenceTransformer:
        if model_name in self._loaded_models:
            self.state.current_model = self._loaded_models[model_name]
        else:
            model = SentenceTransformer(
                model_name_or_path=str(
                    config_data.Path_APP / config_data.StaticPaths_MODELS / model_name
                ),
                device=device,
                local_files_only=False,
                trust_remote_code=True,
            )
            self.state.current_model = model
            self._loaded_models[model_name] = model

        self.model_name = model_name
        return self.state.current_model

    def get_current_model(self) -> Optional[SentenceTransformer]:
        if self.state.current_model is None:
            return None

        return self.state.current_model

    def update_embeddings(self, type_embeddings: str) -> None:
        if self.state.current_model is None or self.model_name is None:
            return None

        data_methods = {
            config_data.Settings_TYPE_RECOMMENDATION[0]: (
                self.get_puds_data,
                config_data.DataframeHeaders_SUBJECTS_FULL_INFO,
                config_data.DataframeHeaders_RU_SUBJECTS[0],
                config_data.StaticPaths_PUDS_EMBEDDINGS,
                config_data.StaticPaths_RU_SUBJECTS,
            ),
            config_data.Settings_TYPE_RECOMMENDATION[1]: (
                self.get_vacancies_data,
                config_data.DataframeHeaders_VACANCIES_FULL_INFO,
                config_data.DataframeHeaders_VACANCIES[1],
                config_data.StaticPaths_VACANCIES_EMBEDDINGS,
                config_data.StaticPaths_RU_VACANCIES,
            ),
        }

        if type_embeddings in data_methods:
            get_data, info_col, name_col, embeddings_path, names_path = data_methods[
                type_embeddings
            ]
            self.state.embeddings, self.state.names = extract_embeddings(
                model_name=self.model_name,
                d_cleaned=get_data(),
                sbert_model=self.state.current_model,
                info_col=info_col,
                name_col=name_col,
                embeddings_path=embeddings_path,
                names_path=names_path,
            )

    def get_embeddings(self) -> tuple[torch.Tensor, pl.DataFrame]:
        if self.state.embeddings.numel() == 0 or self.state.puds_names.is_empty():
            return (torch.empty(0), pl.DataFrame())

        return (self.state.embeddings, self.state.names)

    def get_vacancies_embeddings(self) -> tuple[torch.Tensor, pl.DataFrame]:
        if self.state.embeddings.numel() == 0:
            return torch.empty(0)

        return self.state.embeddings

    def change_model(self, model_name: str, type_embeddings: str) -> None:
        if not config_data.AppSettings_DEV:
            self.load_model(model_name)
            self.update_embeddings(type_embeddings)
