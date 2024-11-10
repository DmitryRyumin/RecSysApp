"""
File: data_init.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: Initial data loading.
License: MIT License
"""

import torch

# Importing necessary components for the Gradio app
from app.config import config_data
from app.data_utils import load_parquet
from app.load_models import SbertModelManager
from app.load_vacancy_models import SkillsExtractor


cosine_similarity = torch.nn.CosineSimilarity()

df_puds_skills = load_parquet(
    path=config_data.Path_APP / config_data.StaticPaths_PUDS_SKILLS,
    drop_duplicates=True,
    subset=config_data.DataframeHeaders_RU_ID,
)

df_courses_grades = load_parquet(
    path=config_data.Path_APP / config_data.StaticPaths_COURSES_GRADES,
    drop_duplicates=True,
    subset=None,
)

model_manager_sbert = SbertModelManager()
model_manager_sbert.change_model(config_data.Models_SBERT[0])

skills_extractor = SkillsExtractor(
    path_to_vacancies_info=config_data.Path_APP / config_data.StaticPaths_VACANCY
)
