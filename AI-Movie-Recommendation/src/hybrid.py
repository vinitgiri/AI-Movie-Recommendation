"""
hybrid.py
---------
Weighted Hybrid Recommendation Model — the main component of the project.

    hybrid_score = content_weight * normalized_content_score
                 + collaborative_weight * normalized_collaborative_score

Content similarity scores and predicted ratings live on different numeric
scales, so each is min-max normalized to [0, 1] *before* the weighted sum is
computed. Handles the cold-start case (new/low-history users) by falling
back to pure content-based recommendations and flags this in the output.
"""

from __future__ import annotations

import pandas as pd

from src import config
from src.collaborative import CollaborativeRecommender, UnknownUserError
from src.content_based import ContentBasedRecommender
from src.utils import get_logger, min_max_normalize

logger = get_logger(__name__)


class HybridRecommender:
    """Combines a ContentBasedRecommender and a CollaborativeRecommender."""

    def __init__(
        self,
        content_model: ContentBasedRecommender,
        collaborative_model: CollaborativeRecommender,
        ratings: pd.DataFrame,
    ):
        self.content_model = content_model
        self.collaborative_model = collaborative_model
        self.ratings = ratings

    @staticmethod
    def _validate_weights(content_weight: float, collaborative_weight: float) -> None:
        total = content_weight + collaborative_weight
        if content_weight < 0 or collaborative_weight < 0:
            raise ValueError("Weights must be non-negative.")
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"content_weight + collaborative_weight must equal 1 (got {total:.3f})."
            )

    def recommend_for_user(
        self,
        user_id: int,
        n: int = config.DEFAULT_TOP_N,
        content_weight: float = config.DEFAULT_CONTENT_WEIGHT,
        collaborative_weight: float = config.DEFAULT_COLLABORATIVE_WEIGHT,
    ) -> pd.DataFrame:
        """
        Generate personalized Top-N recommendations for a known user.

        Returns a DataFrame with columns:
            movieId, title, genres, content_score, collaborative_score,
            predicted_rating, hybrid_score, explanation, fallback_used
        """
        self._validate_weights(content_weight, collaborative_weight)

        if user_id not in self.collaborative_model._user_rated:
            raise UnknownUserError(f"Unknown userId: {user_id}")

        user_ratings = self.ratings[self.ratings["userId"] == user_id]
        already_rated = set(user_ratings["movieId"])
        liked_movie_ids = list(user_ratings.loc[user_ratings["rating"] >= config.RELEVANCE_THRESHOLD, "movieId"])

        fallback_used = not self.collaborative_model.has_sufficient_history(user_id)

        candidate_ids = [
            mid for mid in self.content_model.movies["movieId"] if mid not in already_rated
        ]

        content_scores = self.content_model.score_all_for_profile(liked_movie_ids).reindex(candidate_ids).fillna(0.0)

        if fallback_used:
            logger.info(
                "User %s has < %d ratings; falling back to content-based recommendations.",
                user_id, config.MIN_RATINGS_FOR_COLLABORATIVE,
            )
            collab_scores = pd.Series(0.0, index=candidate_ids)
            effective_content_weight, effective_collab_weight = 1.0, 0.0
        else:
            collab_scores = self.collaborative_model.score_candidates(user_id, candidate_ids)
            effective_content_weight, effective_collab_weight = content_weight, collaborative_weight

        norm_content = pd.Series(min_max_normalize(content_scores.values), index=content_scores.index)
        norm_collab = pd.Series(min_max_normalize(collab_scores.values), index=collab_scores.index)

        hybrid_score = (
            effective_content_weight * norm_content
            + effective_collab_weight * norm_collab
        )

        result = self.content_model.movies.set_index("movieId").loc[candidate_ids][["title", "genres"]].copy()
        result["content_score"] = content_scores
        result["collaborative_score"] = collab_scores
        result["predicted_rating"] = collab_scores  # same underlying value, human-readable alias
        result["hybrid_score"] = hybrid_score
        result["fallback_used"] = fallback_used
        result["_norm_content"] = norm_content
        result["_norm_collab"] = norm_collab
        result = result.sort_values("hybrid_score", ascending=False).head(n).reset_index()
        result = result.drop_duplicates(subset=["movieId"]).reset_index(drop=True)
        result["explanation"] = result.apply(lambda row: self._explain(row, fallback_used), axis=1)
        result = result.drop(columns=["_norm_content", "_norm_collab"])
        return result

    def recommend_similar_to_movie(self, movie_title: str, n: int = config.DEFAULT_TOP_N) -> pd.DataFrame:
        """Pure content-based 'find movies similar to this one' mode."""
        result = self.content_model.get_similar_movies(movie_title, n=n)
        result["explanation"] = "Recommended because it is similar to movies you liked."
        return result

    @staticmethod
    def _explain(row: pd.Series, fallback_used: bool) -> str:
        if fallback_used:
            return (
                "Recommended because it is similar to movies you liked "
                "(limited rating history available)."
            )
        nc = row["_norm_content"]
        ncl = row["_norm_collab"]
        if nc > 0.01 and ncl > 0.01 and abs(nc - ncl) < 0.25:
            return (
                "Recommended using a combination of your rating behavior "
                "and movie similarity."
            )
        if nc >= ncl:
            return "Recommended because it is similar to movies you liked."
        return "Recommended because you rated similar movies highly."
