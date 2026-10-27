"""
collaborative.py
-----------------
Collaborative Filtering module built on scikit-surprise's SVD.

Pipeline:
    (userId, movieId, rating) -> Surprise Dataset -> train/test split
    -> SVD training -> predicted ratings for unseen (user, movie) pairs
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split as surprise_train_test_split

from src import config
from src.utils import get_logger

logger = get_logger(__name__)


class UnknownUserError(KeyError):
    """Raised when a requested userId does not exist in the ratings data."""


class CollaborativeRecommender:
    """
    SVD-based collaborative-filtering recommender.

    Attributes
    ----------
    ratings : pd.DataFrame
        Cleaned ratings table (userId, movieId, rating, timestamp).
    movies : pd.DataFrame
        Cleaned movie catalog, used to attach titles/genres to results.
    model : surprise.SVD
        Fitted SVD model (available after `fit()`).
    """

    def __init__(self, ratings: pd.DataFrame, movies: pd.DataFrame):
        self.ratings = ratings
        self.movies = movies
        self.model: Optional[SVD] = None
        self.trainset = None
        self.testset = None
        self._user_rated: dict[int, set] = (
            ratings.groupby("userId")["movieId"].apply(set).to_dict()
        )
        self._all_movie_ids = movies["movieId"].unique().tolist()

    def fit(self, full_fit: bool = False) -> "CollaborativeRecommender":
        """
        Train the SVD model.

        If `full_fit` is False (default), an 80:20 train/test split (fixed
        seed) is held out so evaluation.py can compute honest RMSE/MAE.
        If True, the model is retrained on 100% of the data for the
        production model used to actually generate recommendations.
        """
        reader = Reader(rating_scale=config.RATING_SCALE)
        data = Dataset.load_from_df(self.ratings[["userId", "movieId", "rating"]], reader)

        self.model = SVD(
            n_factors=config.SVD_N_FACTORS,
            n_epochs=config.SVD_N_EPOCHS,
            lr_all=config.SVD_LR_ALL,
            reg_all=config.SVD_REG_ALL,
            random_state=config.RANDOM_SEED,
        )

        if full_fit:
            self.trainset = data.build_full_trainset()
            self.testset = None
        else:
            self.trainset, self.testset = surprise_train_test_split(
                data, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED
            )

        self.model.fit(self.trainset)
        logger.info(
            "CollaborativeRecommender fit (full_fit=%s): %d users, %d items in trainset",
            full_fit, self.trainset.n_users, self.trainset.n_items,
        )
        return self

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """Predict the rating a user would give a movie using the trained SVD model."""
        if self.model is None:
            raise RuntimeError("Call fit() before requesting predictions.")
        pred = self.model.predict(user_id, movie_id)
        return float(pred.est)

    def has_sufficient_history(self, user_id: int) -> bool:
        """True if the user has enough ratings for collaborative filtering to be meaningful."""
        return len(self._user_rated.get(user_id, set())) >= config.MIN_RATINGS_FOR_COLLABORATIVE

    def recommend(self, user_id: int, n: int = 10) -> pd.DataFrame:
        """
        Return the top-n movies (by predicted rating) for a known user,
        excluding movies the user has already rated.

        Returns a DataFrame with columns:
            movieId, title, genres, predicted_rating, collaborative_score
        """
        if self.model is None:
            raise RuntimeError("Call fit() before requesting recommendations.")
        if user_id not in self._user_rated:
            raise UnknownUserError(f"Unknown userId: {user_id}")

        already_rated = self._user_rated.get(user_id, set())
        candidates = [mid for mid in self._all_movie_ids if mid not in already_rated]

        predictions = [(mid, self.predict_rating(user_id, mid)) for mid in candidates]
        predictions.sort(key=lambda x: x[1], reverse=True)
        top = predictions[:n]

        top_ids = [mid for mid, _ in top]
        preds = [score for _, score in top]

        result = self.movies.set_index("movieId").loc[top_ids][["title", "genres"]].reset_index()
        result["predicted_rating"] = preds
        # collaborative_score mirrors predicted_rating; kept as a separate
        # column so the hybrid module can normalize it independently of the
        # human-readable predicted rating.
        result["collaborative_score"] = preds
        return result

    def score_candidates(self, user_id: int, candidate_movie_ids: list[int]) -> pd.Series:
        """Predicted rating for an arbitrary list of candidate movies for a user."""
        if self.model is None:
            raise RuntimeError("Call fit() before requesting predictions.")
        scores = {mid: self.predict_rating(user_id, mid) for mid in candidate_movie_ids}
        return pd.Series(scores)
