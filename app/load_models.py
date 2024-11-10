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
from app.data_utils import load_puds_data, extract_embeddings


@dataclass
class ModelState:
    current_model: Optional[SentenceTransformer] = None
    puds_embeddings: Optional[torch.Tensor] = field(
        default_factory=lambda: torch.empty(0)
    )
    puds_names: Optional[pl.DataFrame] = field(default_factory=pl.DataFrame)


@dataclass
class BaseModelManager:
    _puds_data: Optional[dict] = field(init=False, default=None)
    state: ModelState = field(default_factory=ModelState)

    def __post_init__(self):
        self._load_puds_data_once()

    @classmethod
    def _load_puds_data_once(cls):
        if cls._puds_data is None:
            df_puds_cleaned, _ = load_puds_data(
                path=config_data.Path_APP / config_data.StaticPaths_PUDS,
                year=config_data.DataframeHeaders_SUBJECTS_YEAR,
                drop_duplicates=True,
                subset=config_data.DataframeHeaders_RU_SUBJECTS[:2],
                full_info_cols=config_data.DataframeHeaders_SUBJECTS_FULL,
            )
            cls._puds_data = df_puds_cleaned.to_dicts()

    def get_puds_data(self) -> dict:
        if self._puds_data is None:
            return {}
        return self._puds_data


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

    def update_embeddings(self) -> None:
        if self.state.current_model is None or self.model_name is None:
            return None

        self.state.puds_embeddings, self.state.puds_names = extract_embeddings(
            model_name=self.model_name,
            d_puds_cleaned=self.get_puds_data(),
            sbert_model=self.state.current_model,
            limit=None,
            force_reload=False,
        )

    def get_embeddings(self) -> tuple[torch.Tensor, pl.DataFrame]:
        if self.state.puds_embeddings.numel() == 0 or self.state.puds_names.is_empty():
            return (torch.empty(0), pl.DataFrame())

        return (self.state.puds_embeddings, self.state.puds_names)

    def change_model(self, model_name: str) -> None:
        self.load_model(model_name)
        self.update_embeddings()
