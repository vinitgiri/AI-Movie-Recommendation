"""
Shared pytest fixtures: a small, deterministic in-memory dataset shaped
exactly like the cleaned MovieLens tables, so tests never depend on the
real ml-1m files being present on disk.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def raw_movies_df() -> pd.DataFrame:
    return pd.DataFrame({
        "movieId": [1, 2, 3, 4, 4, None],
        "title": ["Toy Story (1995)", "Jumanji (1995)", "Grumpier Old Men (1995)",
                   "Heat (1995)", "Heat (1995)", "Bad Row"],
        "genres": ["Animation|Children's|Comedy", "Adventure|Children's|Fantasy",
                    "Comedy|Romance", "Action|Crime|Thriller",
                    "Action|Crime|Thriller", "Comedy"],
    })


@pytest.fixture
def raw_ratings_df() -> pd.DataFrame:
    return pd.DataFrame({
        "userId": [1, 1, 1, 2, 2, 3, 3, 3, 3, 99],
        "movieId": [1, 2, 3, 1, 4, 1, 2, 3, 4, 999],
        "rating": [5.0, 4.0, 3.0, 4.0, 5.0, 2.0, 3.0, 4.0, 5.0, 7.0],
        "timestamp": [978300000] * 10,
    })


@pytest.fixture
def raw_users_df() -> pd.DataFrame:
    return pd.DataFrame({
        "userId": [1, 2, 3],
        "gender": ["F", "M", "M"],
        "age": [25, 35, 18],
        "occupation": [4, 7, 10],
        "zipCode": ["10001", "20002", "30003"],
    })


@pytest.fixture
def clean_movies_df(raw_movies_df) -> pd.DataFrame:
    from src.preprocessing import clean_movies
    return clean_movies(raw_movies_df)


@pytest.fixture
def clean_users_df(raw_users_df) -> pd.DataFrame:
    from src.preprocessing import clean_users
    return clean_users(raw_users_df)


@pytest.fixture
def clean_ratings_df(raw_ratings_df, clean_movies_df, clean_users_df) -> pd.DataFrame:
    from src.preprocessing import clean_ratings
    return clean_ratings(
        raw_ratings_df,
        valid_movie_ids=set(clean_movies_df["movieId"]),
        valid_user_ids=set(clean_users_df["userId"]),
    )
