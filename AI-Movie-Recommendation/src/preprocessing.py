"""
preprocessing.py
-----------------
Loads the raw MovieLens 1M ``.dat`` files, validates and cleans them, and
reports dataset statistics. Every cleaning operation is logged so nothing
is silently discarded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import pandas as pd

from src import config
from src.utils import get_logger

logger = get_logger(__name__)


class DatasetNotFoundError(FileNotFoundError):
    """Raised when the expected MovieLens .dat files are missing."""


@dataclass
class DatasetStats:
    """Container for the headline statistics reported to the UI and logs."""
    n_movies: int
    n_users: int
    n_ratings: int
    avg_rating: float
    rating_distribution: Dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "n_movies": self.n_movies,
            "n_users": self.n_users,
            "n_ratings": self.n_ratings,
            "avg_rating": round(self.avg_rating, 4),
            "rating_distribution": self.rating_distribution,
        }


def check_dataset_exists() -> None:
    """Raise a clear error if any of the three required .dat files is missing."""
    missing = [p for p in (config.MOVIES_FILE, config.RATINGS_FILE, config.USERS_FILE) if not p.exists()]
    if missing:
        names = ", ".join(str(p) for p in missing)
        raise DatasetNotFoundError(
            f"Missing MovieLens 1M file(s): {names}. "
            f"Download ml-1m.zip from https://grouplens.org/datasets/movielens/1m/ "
            f"and extract movies.dat, ratings.dat, users.dat into {config.DATA_DIR}"
        )


def load_movies() -> pd.DataFrame:
    """Load movies.dat (movieId::title::genres)."""
    df = pd.read_csv(
        config.MOVIES_FILE, sep="::", engine="python",
        names=["movieId", "title", "genres"],
        encoding="latin-1",
    )
    logger.info("Loaded movies.dat: %d rows", len(df))
    return df


def load_ratings() -> pd.DataFrame:
    """Load ratings.dat (userId::movieId::rating::timestamp)."""
    df = pd.read_csv(
        config.RATINGS_FILE, sep="::", engine="python",
        names=["userId", "movieId", "rating", "timestamp"],
        encoding="latin-1",
    )
    logger.info("Loaded ratings.dat: %d rows", len(df))
    return df


def load_users() -> pd.DataFrame:
    """Load users.dat (userId::gender::age::occupation::zipCode)."""
    df = pd.read_csv(
        config.USERS_FILE, sep="::", engine="python",
        names=["userId", "gender", "age", "occupation", "zipCode"],
        encoding="latin-1",
    )
    logger.info("Loaded users.dat: %d rows", len(df))
    return df


def clean_movies(movies: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the movies table. Logs every operation performed."""
    df = movies.copy()
    n_before = len(df)

    n_missing = df[["movieId", "title", "genres"]].isnull().any(axis=1).sum()
    if n_missing:
        logger.info("clean_movies: dropping %d row(s) with missing core fields", n_missing)
        df = df.dropna(subset=["movieId", "title", "genres"])

    n_dupe = df.duplicated(subset=["movieId"]).sum()
    if n_dupe:
        logger.info("clean_movies: dropping %d duplicate movieId row(s)", n_dupe)
        df = df.drop_duplicates(subset=["movieId"])

    df["movieId"] = df["movieId"].astype(int)
    df["title"] = df["title"].astype(str).str.strip()

    # genres arrive pipe-separated, e.g. "Animation|Children's|Comedy".
    # "(no genres listed)" is MovieLens's own sentinel for missing genre data.
    df["genres"] = df["genres"].astype(str).str.strip()
    n_no_genre = (df["genres"] == "(no genres listed)").sum()
    if n_no_genre:
        logger.info("clean_movies: %d movie(s) have no listed genres (kept, treated as empty)", n_no_genre)
    df["genres_clean"] = df["genres"].replace("(no genres listed)", "").str.replace("|", " ", regex=False)

    df = df.reset_index(drop=True)
    logger.info("clean_movies: %d -> %d rows after cleaning", n_before, len(df))
    return df


def clean_ratings(ratings: pd.DataFrame, valid_movie_ids: set, valid_user_ids: set) -> pd.DataFrame:
    """Validate and clean the ratings table. Logs every operation performed."""
    df = ratings.copy()
    n_before = len(df)

    n_missing = df.isnull().any(axis=1).sum()
    if n_missing:
        logger.info("clean_ratings: dropping %d row(s) with missing fields", n_missing)
        df = df.dropna()

    n_dupe = df.duplicated(subset=["userId", "movieId"]).sum()
    if n_dupe:
        logger.info("clean_ratings: dropping %d duplicate (userId, movieId) row(s)", n_dupe)
        df = df.drop_duplicates(subset=["userId", "movieId"])

    df["userId"] = df["userId"].astype(int)
    df["movieId"] = df["movieId"].astype(int)
    df["rating"] = df["rating"].astype(float)

    n_bad_range = (~df["rating"].between(1, 5)).sum()
    if n_bad_range:
        logger.info("clean_ratings: dropping %d row(s) with rating outside [1, 5]", n_bad_range)
        df = df[df["rating"].between(1, 5)]

    n_orphan_movie = (~df["movieId"].isin(valid_movie_ids)).sum()
    if n_orphan_movie:
        logger.info("clean_ratings: dropping %d row(s) referencing unknown movieId", n_orphan_movie)
        df = df[df["movieId"].isin(valid_movie_ids)]

    n_orphan_user = (~df["userId"].isin(valid_user_ids)).sum()
    if n_orphan_user:
        logger.info("clean_ratings: dropping %d row(s) referencing unknown userId", n_orphan_user)
        df = df[df["userId"].isin(valid_user_ids)]

    df = df.reset_index(drop=True)
    logger.info("clean_ratings: %d -> %d rows after cleaning", n_before, len(df))
    return df


def clean_users(users: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the users table."""
    df = users.copy()
    n_before = len(df)

    n_dupe = df.duplicated(subset=["userId"]).sum()
    if n_dupe:
        logger.info("clean_users: dropping %d duplicate userId row(s)", n_dupe)
        df = df.drop_duplicates(subset=["userId"])

    df["userId"] = df["userId"].astype(int)
    df = df.reset_index(drop=True)
    logger.info("clean_users: %d -> %d rows after cleaning", n_before, len(df))
    return df


def compute_stats(movies: pd.DataFrame, ratings: pd.DataFrame, users: pd.DataFrame) -> DatasetStats:
    """Compute the headline dataset statistics used by both train.py and the UI."""
    dist = ratings["rating"].round().astype(int).value_counts().sort_index().to_dict()
    return DatasetStats(
        n_movies=movies["movieId"].nunique(),
        n_users=users["userId"].nunique(),
        n_ratings=len(ratings),
        avg_rating=float(ratings["rating"].mean()) if len(ratings) else 0.0,
        rating_distribution={int(k): int(v) for k, v in dist.items()},
    )


def run_preprocessing_pipeline() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, DatasetStats]:
    """
    Full pipeline: check -> load -> clean -> validate consistency -> stats.
    Returns (movies, ratings, users, stats).
    """
    check_dataset_exists()

    movies_raw = load_movies()
    ratings_raw = load_ratings()
    users_raw = load_users()

    movies = clean_movies(movies_raw)
    users = clean_users(users_raw)
    ratings = clean_ratings(ratings_raw, valid_movie_ids=set(movies["movieId"]), valid_user_ids=set(users["userId"]))

    stats = compute_stats(movies, ratings, users)
    logger.info(
        "Dataset ready: %d movies, %d users, %d ratings, avg rating %.3f",
        stats.n_movies, stats.n_users, stats.n_ratings, stats.avg_rating,
    )
    return movies, ratings, users, stats
