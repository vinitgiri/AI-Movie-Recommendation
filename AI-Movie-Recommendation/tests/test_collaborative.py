import pytest

from src.collaborative import CollaborativeRecommender, UnknownUserError


def test_fit_produces_a_model(clean_ratings_df, clean_movies_df):
    model = CollaborativeRecommender(clean_ratings_df, clean_movies_df).fit(full_fit=True)
    assert model.model is not None


def test_predict_rating_returns_value_in_scale(clean_ratings_df, clean_movies_df):
    model = CollaborativeRecommender(clean_ratings_df, clean_movies_df).fit(full_fit=True)
    user_id = clean_ratings_df["userId"].iloc[0]
    movie_id = clean_movies_df["movieId"].iloc[0]
    pred = model.predict_rating(user_id, movie_id)
    assert 1.0 <= pred <= 5.0


def test_recommend_excludes_already_rated(clean_ratings_df, clean_movies_df):
    model = CollaborativeRecommender(clean_ratings_df, clean_movies_df).fit(full_fit=True)
    user_id = clean_ratings_df["userId"].iloc[0]
    already_rated = set(clean_ratings_df.loc[clean_ratings_df["userId"] == user_id, "movieId"])
    result = model.recommend(user_id, n=10)
    assert not set(result["movieId"]).intersection(already_rated)


def test_recommend_unknown_user_raises(clean_ratings_df, clean_movies_df):
    model = CollaborativeRecommender(clean_ratings_df, clean_movies_df).fit(full_fit=True)
    with pytest.raises(UnknownUserError):
        model.recommend(user_id=987654, n=5)


def test_has_sufficient_history_reflects_rating_count(clean_ratings_df, clean_movies_df):
    model = CollaborativeRecommender(clean_ratings_df, clean_movies_df).fit(full_fit=True)
    user_id = clean_ratings_df["userId"].iloc[0]
    n_ratings = (clean_ratings_df["userId"] == user_id).sum()
    from src import config
    expected = n_ratings >= config.MIN_RATINGS_FOR_COLLABORATIVE
    assert model.has_sufficient_history(user_id) == expected
