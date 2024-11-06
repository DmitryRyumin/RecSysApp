"""
File: load_models.py
Author: Dmitry Ryumin
Description: Classes for loading models and updating embeddings.
License: MIT License
"""

import torch
from transformers import AutoTokenizer, AutoModel
from scipy.spatial.distance import cosine
import pandas as pd
import numpy as np

# Importing necessary components for the Gradio app
from app.config import config_data


def load_embeddings(path):
    df = pd.read_parquet(path)

    return df


class EmbeddingExtractor:
    def __init__(self, model, tokenizer, initial_df, similarity_metric=cosine):
        self.embeddings = {}
        self.model = model
        self.tokenizer = tokenizer
        self.similarity_metric = similarity_metric

        self._initialize_embeddings(initial_df)

    def _initialize_embeddings(self, initial_df):
        for _, row in initial_df.iterrows():
            name = row["with_name"]
            emb = row["embedding"]

            self.embeddings[name] = emb

    def extract(self, text):
        if text in self.embeddings:
            return self.embeddings[text]

        encoded_input = self.tokenizer(
            [text], padding=True, truncation=True, max_length=64, return_tensors="pt"
        )
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        embedding = model_output.pooler_output[0].numpy().astype(np.float32)

        self.embeddings[text] = embedding

        return embedding

    def similarity(self, emb1, emb2):
        return 1 - self.similarity_metric(emb1, emb2)


class VacancyFinder:
    def __init__(self, embedding_extractor, initial_df):
        self.embedding_extractor = embedding_extractor
        self.titles = {}
        self.vacancy_stats_by_title = {}

        self._load_vacancies(initial_df)

    def _load_vacancies(self, initial_df):
        titles = list(set(initial_df.parent.values))

        for title in titles:
            self.titles[title] = self.embedding_extractor.extract(title)
            self.vacancy_stats_by_title[title] = []

            for _, row in initial_df[initial_df.parent == title].iterrows():
                name = row["with_name"]
                key_skills = row["key_skills"]
                id_ = row["id"]

                self.vacancy_stats_by_title[title].append(
                    [name, key_skills, id_, self.embedding_extractor.extract(name)]
                )

    def _select_best_titles(self, emb, amount):
        stats = []
        for title_name, title_emb in self.titles.items():
            stats.append(
                [
                    title_name,
                    title_emb,
                    self.embedding_extractor.similarity(emb, title_emb),
                ]
            )

        return sorted(stats, key=lambda x: -x[-1])[:amount]

    def _select_best_vacancies(self, emb, titles, amount):
        stats = []
        for title in titles:
            for (
                vacancy_name,
                key_skills,
                vacancy_id,
                vacancy_emb,
            ) in self.vacancy_stats_by_title[title]:
                stats.append(
                    [
                        vacancy_name,
                        key_skills,
                        vacancy_id,
                        vacancy_emb,
                        title,
                        self.embedding_extractor.similarity(emb, vacancy_emb),
                    ]
                )

        return sorted(stats, key=lambda x: -x[-1])[:amount]

    def get_best_vacancies(self, vacancy_name, nearest_titles=3, amount=20):
        emb = self.embedding_extractor.extract(vacancy_name)
        titles = self._select_best_titles(emb, nearest_titles)
        title_names = [title_name for title_name, _, _ in titles]

        best_vacancies = self._select_best_vacancies(emb, title_names, amount)
        return best_vacancies


class SkillsExtractor:
    def __init__(
        self,
        path_to_vacancies_info,
        model_path=str(
            config_data.Path_APP
            / config_data.StaticPaths_MODELS
            / config_data.Models_SBERT_VACANCY[0]
        ),
        tokenizer_path=str(
            config_data.Path_APP
            / config_data.StaticPaths_MODELS
            / config_data.Models_SBERT_VACANCY[0]
        ),
    ):
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        model = AutoModel.from_pretrained(model_path)
        emb_df = load_embeddings(path_to_vacancies_info)

        self.embedding_extractor = EmbeddingExtractor(model, tokenizer, emb_df)
        self.vacancy_finder = VacancyFinder(self.embedding_extractor, emb_df)

    def key_skills_for_profession(
        self,
        profession,
        max_skills=100,
        min_frequency=3,
        nearest_vacancies=50,
        nearest_titles=5,
        filter_near=True,
    ):
        all_key_skills = []
        for _, key_skills, _, _, _, _ in self.vacancy_finder.get_best_vacancies(
            profession, amount=nearest_vacancies, nearest_titles=nearest_titles
        ):
            all_key_skills.extend(key_skills)

        selected_skills = []
        counted_skills = {}

        for skill in all_key_skills:
            found = False
            for selected_skill in selected_skills:
                if filter_near:
                    selected_skill_emb = self.embedding_extractor.extract(
                        selected_skill
                    )
                    skill_emb = self.embedding_extractor.extract(skill)
                    similarity = self.embedding_extractor.similarity(
                        skill_emb, selected_skill_emb
                    )
                else:
                    if skill == selected_skill:
                        similarity = 1.0
                    else:
                        similarity = 0.0

                if similarity > 0.9:
                    found = True
                    counted_skills[selected_skill] += 1
                    break

            if not found:
                selected_skills.append(skill)
                counted_skills[skill] = 1

        result_skills = []
        for skill in sorted(selected_skills, key=lambda x: -counted_skills[x]):
            amount = counted_skills[skill]
            if len(result_skills) >= max_skills or amount < min_frequency:
                break
            else:
                result_skills.append(skill)

        return result_skills
