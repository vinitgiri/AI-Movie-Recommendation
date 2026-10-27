"""
content_based.py
-----------------
Content-Based Filtering module.

Pipeline:
    genres (pipe-separated) -> space-separated text -> TF-IDF vectors
    -> cosine similarity -> movie-to-movie similarity matrix

The similarity matrix is the basis for both "find movies similar to X" and
the content-side signal of the hybrid model.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.utils import get_logger

logger = get_logger(__name__)


class MovieNotFoundError(KeyError):
    """Raised when a requested movie title does not exist in the catalog."""


class ContentBasedRecommender:
    """
    TF-IDF + cosine-similarity recommender over movie genres.

    Attributes
    ----------
    movies : pd.DataFrame
        Cleaned movie catalog with a `genres_clean` text column.
    tfidf_vectorizer : TfidfVectorizer
        Fitted vectorizer (available after `fit()`).
    tfidf_matrix : scipy.sparse matrix
        TF-IDF feature matrix, one row per movie.
    similarity_matrix : np.ndarray
        Dense movie-to-movie cosine similarity matrix.
    """

    def __init__(self, movies: pd.DataFrame):
        if "genres_clean" not in movies.columns:
            raise ValueError("movies dataframe must contain a 'genres_clean' text column")
        self.movies = movies.reset_index(drop=True)
        self._id_to_index = {mid: idx for idx, mid in enumerate(self.movies["movieId"])}
        self._title_to_index = {t.lower(): idx for idx, t in enumerate(self.movies["title"])}

        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.similarity_matrix: Optional[np.ndarray] = None

    def fit(self) -> "ContentBasedRecommender":
        """Fit the TF-IDF vectorizer on genre text and compute cosine similarity."""
        self.tfidf_vectorizer = TfidfVectorizer(token_pattern=r"[A-Za-z0-9'\-]+")
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movies["genres_clean"])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
        logger.info(
            "ContentBasedRecommender fit: %d movies, %d TF-IDF features",
            self.tfidf_matrix.shape[0], self.tfidf_matrix.shape[1],
        )
        return self

    def _resolve_index(self, movie_title: str) -> int:
        idx = self._title_to_index.get(movie_title.strip().lower())
        if idx is None:
            raise MovieNotFoundError(f"Movie title not found in catalog: {movie_title!r}")
        return idx

    def get_similar_movies(self, movie_title: str, n: int = 10) -> pd.DataFrame:
        """
        Return the top-n movies most similar (by genre) to `movie_title`.

        Returns a DataFrame with columns: movieId, title, genres, content_score.
        Raises MovieNotFoundError for an unknown title.
        """
        if self.similarity_matrix is None:
            raise RuntimeError("Call fit() before requesting recommendations.")

        idx = self._resolve_index(movie_title)
        sims = self.similarity_matrix[idx]

        order = np.argsort(-sims)
        order = order[order != idx]  # never recommend the movie itself
        order = order[:n]

        result = self.movies.iloc[order][["movieId", "title", "genres"]].copy()
        result["content_score"] = sims[order]
        return result.reset_index(drop=True)

    # Alias required by the project spec.
    def recommend(self, movie_title: str, n: int = 10) -> pd.DataFrame:
        return self.get_similar_movies(movie_title, n=n)

    def score_all_for_profile(self, liked_movie_ids: list[int]) -> pd.Series:
        """
        Build a content-based affinity score for every movie in the catalog,
        given a list of movieIds the user is known to like (e.g. rated >= 4).

        The score for each candidate movie is its mean cosine similarity to
        the user's liked movies. Used as the content-side signal for a known
        user inside the hybrid model.
        """
        if self.similarity_matrix is None:
            raise RuntimeError("Call fit() before requesting recommendations.")

        liked_indices = [self._id_to_index[mid] for mid in liked_movie_ids if mid in self._id_to_index]
        if not liked_indices:
            return pd.Series(np.zeros(len(self.movies)), index=self.movies["movieId"])

        scores = self.similarity_matrix[liked_indices].mean(axis=0)
        return pd.Series(scores, index=self.movies["movieId"])
