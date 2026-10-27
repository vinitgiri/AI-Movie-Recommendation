import pandas as pd
import pytest

from src.preprocessing import check_dataset_exists, clean_movies, clean_ratings, clean_users, compute_stats
from src.preprocessing import DatasetNotFoundError
from src import config


def test_clean_movies_drops_missing_and_duplicates(raw_movies_df):
    result = clean_movies(raw_movies_df)
    # one row had a null movieId -> dropped; one duplicate movieId=4 -> deduped
    assert len(result) == 4
    assert result["movieId"].is_unique
    assert result["movieId"].notnull().all()


def test_clean_movies_builds_space_separated_genre_text(raw_movies_df):
    result = clean_movies(raw_movies_df)
    row = result[result["movieId"] == 1].iloc[0]
    assert "|" not in row["genres_clean"]
    assert "Animation" in row["genres_clean"]


def test_clean_ratings_drops_out_of_range_and_orphans(raw_ratings_df, clean_movies_df, clean_users_df):
    result = clean_ratings(
        raw_ratings_df,
        valid_movie_ids=set(clean_movies_df["movieId"]),
        valid_user_ids=set(clean_users_df["userId"]),
    )
    # userId=99 / movieId=999 is an orphan; rating=7.0 is out of [1,5] range
    assert 99 not in result["userId"].values
    assert 999 not in result["movieId"].values
    assert result["rating"].between(1, 5).all()


def test_clean_users_dedupes(raw_users_df):
    dupe = pd.concat([raw_users_df, raw_users_df.iloc[[0]]], ignore_index=True)
    result = clean_users(dupe)
    assert result["userId"].is_unique


def test_compute_stats_matches_inputs(clean_movies_df, clean_ratings_df, clean_users_df):
    stats = compute_stats(clean_movies_df, clean_ratings_df, clean_users_df)
    assert stats.n_movies == clean_movies_df["movieId"].nunique()
    assert stats.n_users == clean_users_df["userId"].nunique()
    assert stats.n_ratings == len(clean_ratings_df)
    assert 1.0 <= stats.avg_rating <= 5.0


def test_check_dataset_exists_raises_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MOVIES_FILE", tmp_path / "movies.dat")
    monkeypatch.setattr(config, "RATINGS_FILE", tmp_path / "ratings.dat")
    monkeypatch.setattr(config, "USERS_FILE", tmp_path / "users.dat")
    with pytest.raises(DatasetNotFoundError):
        check_dataset_exists()
