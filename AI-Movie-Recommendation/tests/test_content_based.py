import pytest

from src.content_based import ContentBasedRecommender, MovieNotFoundError


def test_fit_builds_similarity_matrix(clean_movies_df):
    model = ContentBasedRecommender(clean_movies_df).fit()
    n = len(clean_movies_df)
    assert model.similarity_matrix.shape == (n, n)


def test_get_similar_movies_excludes_itself(clean_movies_df):
    model = ContentBasedRecommender(clean_movies_df).fit()
    title = clean_movies_df.iloc[0]["title"]
    result = model.get_similar_movies(title, n=10)
    assert title not in result["title"].values


def test_get_similar_movies_returns_expected_columns(clean_movies_df):
    model = ContentBasedRecommender(clean_movies_df).fit()
    title = clean_movies_df.iloc[0]["title"]
    result = model.get_similar_movies(title, n=2)
    assert set(["movieId", "title", "genres", "content_score"]).issubset(result.columns)


def test_invalid_movie_title_raises(clean_movies_df):
    model = ContentBasedRecommender(clean_movies_df).fit()
    with pytest.raises(MovieNotFoundError):
        model.get_similar_movies("This Movie Does Not Exist (1900)")


def test_score_all_for_profile_handles_empty_profile(clean_movies_df):
    model = ContentBasedRecommender(clean_movies_df).fit()
    scores = model.score_all_for_profile([])
    assert (scores == 0).all()


def test_recommend_is_alias_for_get_similar_movies(clean_movies_df):
    model = ContentBasedRecommender(clean_movies_df).fit()
    title = clean_movies_df.iloc[0]["title"]
    a = model.recommend(title, n=3)
    b = model.get_similar_movies(title, n=3)
    assert a["movieId"].tolist() == b["movieId"].tolist()
