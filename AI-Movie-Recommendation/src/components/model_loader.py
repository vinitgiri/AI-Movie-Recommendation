"""
src/components/model_loader.py
-------------------------------
Shared, cached model loading used across all pages.
Returns models via st.cache_resource so they are loaded only once.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import joblib
import streamlit as st

from src import config
from src.collaborative import CollaborativeRecommender
from src.content_based import ContentBasedRecommender
from src.hybrid import HybridRecommender


@st.cache_resource(show_spinner="Loading AI models...")
def load_models():
    """
    Load all pre-trained models from disk.

    Returns:
        (movies, ratings, users, hybrid_model, collab_model, missing_files)
        If missing_files is non-empty, models are not available.
    """
    required = [
        config.TFIDF_VECTORIZER_PATH,
        config.TFIDF_MATRIX_PATH,
        config.COSINE_SIM_PATH,
        config.SVD_MODEL_PATH,
        config.MOVIES_CLEAN_PATH,
        config.RATINGS_CLEAN_PATH,
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        return None, None, None, None, None, missing

    movies = joblib.load(config.MOVIES_CLEAN_PATH)
    ratings = joblib.load(config.RATINGS_CLEAN_PATH)

    users = None
    if config.USERS_CLEAN_PATH.exists():
        users = joblib.load(config.USERS_CLEAN_PATH)

    content_model = ContentBasedRecommender(movies)
    content_model.tfidf_vectorizer = joblib.load(config.TFIDF_VECTORIZER_PATH)
    content_model.tfidf_matrix = joblib.load(config.TFIDF_MATRIX_PATH)
    content_model.similarity_matrix = joblib.load(config.COSINE_SIM_PATH)

    collab_model = CollaborativeRecommender(ratings, movies)
    collab_model.model = joblib.load(config.SVD_MODEL_PATH)

    hybrid_model = HybridRecommender(content_model, collab_model, ratings)
    return movies, ratings, users, hybrid_model, collab_model, []


@st.cache_data(show_spinner=False)
def load_metrics() -> Optional[dict]:
    """Load metrics.json if available."""
    if config.METRICS_JSON_PATH.exists():
        with open(config.METRICS_JSON_PATH) as f:
            return json.load(f)
    return None


def try_recommend(func, *args, **kwargs):
    """Run a recommender function. Returns (result, error_message)."""
    try:
        return func(*args, **kwargs), None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def models_missing_error(missing: list):
    """Render a user-friendly error when models haven't been trained."""
    st.error(
        ":material/model_training: **Recommendation models haven't been trained yet.**  \n"
        "Run `python train.py` after placing the MovieLens 1M `.dat` files in `data/ml-1m/`.",
        icon=":material/error:",
    )
    with st.expander("Missing files", icon=":material/folder_open:"):
        for p in missing:
            st.code(str(p))
