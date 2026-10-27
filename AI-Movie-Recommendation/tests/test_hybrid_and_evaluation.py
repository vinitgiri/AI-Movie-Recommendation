import pytest

from src.collaborative import CollaborativeRecommender, UnknownUserError
from src.content_based import ContentBasedRecommender
from src.hybrid import HybridRecommender
from src.evaluation import calculate_mae, calculate_rmse, precision_at_k, recall_at_k
from src.utils import min_max_normalize


@pytest.fixture
def hybrid_model(clean_movies_df, clean_ratings_df):
    content_model = ContentBasedRecommender(clean_movies_df).fit()
    collab_model = CollaborativeRecommender(clean_ratings_df, clean_movies_df).fit(full_fit=True)
    return HybridRecommender(content_model, collab_model, clean_ratings_df)


def test_weights_must_sum_to_one(hybrid_model, clean_ratings_df):
    user_id = clean_ratings_df["userId"].iloc[0]
    with pytest.raises(ValueError):
        hybrid_model.recommend_for_user(user_id, content_weight=0.9, collaborative_weight=0.9)


def test_recommend_for_user_excludes_already_rated(hybrid_model, clean_ratings_df):
    user_id = clean_ratings_df["userId"].iloc[0]
    already_rated = set(clean_ratings_df.loc[clean_ratings_df["userId"] == user_id, "movieId"])
    result = hybrid_model.recommend_for_user(user_id, n=10)
    assert not set(result["movieId"]).intersection(already_rated)


def test_recommend_for_user_no_duplicates(hybrid_model, clean_ratings_df):
    user_id = clean_ratings_df["userId"].iloc[0]
    result = hybrid_model.recommend_for_user(user_id, n=10)
    assert result["movieId"].is_unique


def test_recommend_for_user_unknown_user_raises(hybrid_model):
    with pytest.raises(UnknownUserError):
        hybrid_model.recommend_for_user(user_id=987654, n=5)


def test_recommend_similar_to_movie(hybrid_model, clean_movies_df):
    title = clean_movies_df.iloc[0]["title"]
    result = hybrid_model.recommend_similar_to_movie(title, n=3)
    assert "explanation" in result.columns
    assert title not in result["title"].values


# --- evaluation.py -----------------------------------------------------

def test_rmse_zero_for_perfect_predictions():
    assert calculate_rmse([1, 2, 3], [1, 2, 3]) == 0.0


def test_mae_matches_known_value():
    assert calculate_mae([1, 2, 3], [2, 2, 2]) == pytest.approx(2 / 3)


def test_precision_at_k():
    recommended = [1, 2, 3, 4, 5]
    relevant = {2, 4, 6}
    assert precision_at_k(recommended, relevant, k=5) == pytest.approx(2 / 5)


def test_recall_at_k():
    recommended = [1, 2, 3, 4, 5]
    relevant = {2, 4, 6}
    assert recall_at_k(recommended, relevant, k=5) == pytest.approx(2 / 3)


def test_recall_at_k_empty_relevant_returns_zero():
    assert recall_at_k([1, 2, 3], set(), k=3) == 0.0


def test_min_max_normalize_constant_array_returns_half():
    result = min_max_normalize([5, 5, 5])
    assert (result == 0.5).all()


def test_min_max_normalize_range_is_zero_to_one():
    result = min_max_normalize([1, 2, 3, 10])
    assert result.min() == 0.0
    assert result.max() == 1.0
