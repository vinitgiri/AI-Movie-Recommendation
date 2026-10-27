"""
evaluation.py
-------------
Evaluation framework shared across Content-Based, Collaborative, and Hybrid
models: RMSE, MAE, Precision@K, Recall@K.

Rating-prediction metrics (RMSE/MAE) are not meaningful for pure
content-based ranking (it has no notion of a 1-5 predicted rating), so those
cells are reported as "N/A" rather than invented. Precision@K/Recall@K are
meaningful for all three because each can produce a ranked Top-N list.
"""

from __future__ import annotations

import json
import random
from typing import Iterable

import numpy as np
import pandas as pd

from src import config
from src.collaborative import CollaborativeRecommender
from src.content_based import ContentBasedRecommender
from src.utils import get_logger, min_max_normalize, safe_divide

logger = get_logger(__name__)

NOT_APPLICABLE = "N/A"

# Cap on the number of test users sampled for Precision@K / Recall@K so
# evaluation stays fast on the full MovieLens 1M dataset while remaining a
# statistically reasonable sample.
MAX_EVAL_USERS = 300


def calculate_rmse(y_true: Iterable[float], y_pred: Iterable[float]) -> float:
    """Root Mean Squared Error between true and predicted ratings."""
    y_true = np.asarray(list(y_true), dtype=float)
    y_pred = np.asarray(list(y_pred), dtype=float)
    if y_true.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_mae(y_true: Iterable[float], y_pred: Iterable[float]) -> float:
    """Mean Absolute Error between true and predicted ratings."""
    y_true = np.asarray(list(y_true), dtype=float)
    y_pred = np.asarray(list(y_pred), dtype=float)
    if y_true.size == 0:
        return float("nan")
    return float(np.mean(np.abs(y_true - y_pred)))


def precision_at_k(recommended_ids: list, relevant_ids: set, k: int) -> float:
    """Fraction of the top-k recommended items that are actually relevant."""
    if k == 0:
        return 0.0
    top_k = recommended_ids[:k]
    hits = sum(1 for mid in top_k if mid in relevant_ids)
    return safe_divide(hits, len(top_k))


def recall_at_k(recommended_ids: list, relevant_ids: set, k: int) -> float:
    """Fraction of all relevant items that appear in the top-k recommendations."""
    if not relevant_ids:
        return 0.0
    top_k = recommended_ids[:k]
    hits = sum(1 for mid in top_k if mid in relevant_ids)
    return safe_divide(hits, len(relevant_ids))


def _eval_users(train_df: pd.DataFrame, test_df: pd.DataFrame) -> list[int]:
    """Users present in both train and test with at least one relevant (>=threshold) test item."""
    relevant_test = test_df[test_df["rating"] >= config.RELEVANCE_THRESHOLD]
    candidate_users = sorted(set(relevant_test["userId"]) & set(train_df["userId"]))
    rng = random.Random(config.RANDOM_SEED)
    if len(candidate_users) > MAX_EVAL_USERS:
        candidate_users = rng.sample(candidate_users, MAX_EVAL_USERS)
    return candidate_users


def evaluate_content_based(
    content_model: ContentBasedRecommender,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    k_values: list[int],
) -> dict:
    """Precision@K / Recall@K for the content-based model. RMSE/MAE are N/A."""
    users = _eval_users(train_df, test_df)
    metrics = {f"precision_at_{k}": [] for k in k_values}
    metrics.update({f"recall_at_{k}": [] for k in k_values})

    all_movie_ids = set(content_model.movies["movieId"])

    for user_id in users:
        train_rated = set(train_df.loc[train_df["userId"] == user_id, "movieId"])
        liked = list(train_df.loc[
            (train_df["userId"] == user_id) & (train_df["rating"] >= config.RELEVANCE_THRESHOLD), "movieId"
        ])
        relevant = set(test_df.loc[
            (test_df["userId"] == user_id) & (test_df["rating"] >= config.RELEVANCE_THRESHOLD), "movieId"
        ])
        if not liked or not relevant:
            continue

        candidates = list(all_movie_ids - train_rated)
        scores = content_model.score_all_for_profile(liked).reindex(candidates).fillna(0.0)
        ranked = list(scores.sort_values(ascending=False).index)

        for k in k_values:
            metrics[f"precision_at_{k}"].append(precision_at_k(ranked, relevant, k))
            metrics[f"recall_at_{k}"].append(recall_at_k(ranked, relevant, k))

    result = {"rmse": NOT_APPLICABLE, "mae": NOT_APPLICABLE}
    for key, values in metrics.items():
        result[key] = round(float(np.mean(values)), 4) if values else NOT_APPLICABLE
    result["n_eval_users"] = len(users)
    return result


def evaluate_collaborative(
    collaborative_model: CollaborativeRecommender,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    k_values: list[int],
) -> dict:
    """RMSE / MAE (from the held-out test set) plus Precision@K / Recall@K."""
    if collaborative_model.testset is None:
        raise RuntimeError("CollaborativeRecommender must be fit with full_fit=False to evaluate RMSE/MAE.")

    predictions = collaborative_model.model.test(collaborative_model.testset)
    y_true = [p.r_ui for p in predictions]
    y_pred = [p.est for p in predictions]
    rmse = calculate_rmse(y_true, y_pred)
    mae = calculate_mae(y_true, y_pred)

    users = _eval_users(train_df, test_df)
    metrics = {f"precision_at_{k}": [] for k in k_values}
    metrics.update({f"recall_at_{k}": [] for k in k_values})
    all_movie_ids = collaborative_model._all_movie_ids

    for user_id in users:
        train_rated = set(train_df.loc[train_df["userId"] == user_id, "movieId"])
        relevant = set(test_df.loc[
            (test_df["userId"] == user_id) & (test_df["rating"] >= config.RELEVANCE_THRESHOLD), "movieId"
        ])
        if not relevant:
            continue
        candidates = [mid for mid in all_movie_ids if mid not in train_rated]
        scored = collaborative_model.score_candidates(user_id, candidates)
        ranked = list(scored.sort_values(ascending=False).index)

        for k in k_values:
            metrics[f"precision_at_{k}"].append(precision_at_k(ranked, relevant, k))
            metrics[f"recall_at_{k}"].append(recall_at_k(ranked, relevant, k))

    result = {"rmse": round(rmse, 4), "mae": round(mae, 4)}
    for key, values in metrics.items():
        result[key] = round(float(np.mean(values)), 4) if values else NOT_APPLICABLE
    result["n_eval_users"] = len(users)
    return result


def evaluate_hybrid(
    content_model: ContentBasedRecommender,
    collaborative_model: CollaborativeRecommender,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    k_values: list[int],
    content_weight: float = config.DEFAULT_CONTENT_WEIGHT,
    collaborative_weight: float = config.DEFAULT_COLLABORATIVE_WEIGHT,
) -> dict:
    """
    RMSE / MAE for the hybrid model, plus Precision@K / Recall@K.

    RMSE/MAE are computed by linearly rescaling the normalized hybrid score
    (range [0, 1]) back onto the rating scale [1, 5] and comparing against
    the actual held-out ratings. This is a reasonable approximation, not an
    exact rating prediction, and is documented as such in the README.
    """
    users = _eval_users(train_df, test_df)
    metrics = {f"precision_at_{k}": [] for k in k_values}
    metrics.update({f"recall_at_{k}": [] for k in k_values})
    all_movie_ids = set(content_model.movies["movieId"])

    y_true_scaled, y_pred_scaled = [], []

    for user_id in users:
        train_rated = set(train_df.loc[train_df["userId"] == user_id, "movieId"])
        liked = list(train_df.loc[
            (train_df["userId"] == user_id) & (train_df["rating"] >= config.RELEVANCE_THRESHOLD), "movieId"
        ])
        relevant = set(test_df.loc[
            (test_df["userId"] == user_id) & (test_df["rating"] >= config.RELEVANCE_THRESHOLD), "movieId"
        ])
        if not relevant:
            continue

        candidates = list(all_movie_ids - train_rated)
        content_scores = content_model.score_all_for_profile(liked).reindex(candidates).fillna(0.0)
        collab_scores = collaborative_model.score_candidates(user_id, candidates)

        norm_content = pd.Series(min_max_normalize(content_scores.values), index=content_scores.index)
        norm_collab = pd.Series(min_max_normalize(collab_scores.values), index=collab_scores.index)
        hybrid_score = content_weight * norm_content + collaborative_weight * norm_collab
        ranked = list(hybrid_score.sort_values(ascending=False).index)

        for k in k_values:
            metrics[f"precision_at_{k}"].append(precision_at_k(ranked, relevant, k))
            metrics[f"recall_at_{k}"].append(recall_at_k(ranked, relevant, k))

        # RMSE/MAE approximation via rescaled hybrid score, for the test movies actually rated.
        test_movie_ids = set(test_df.loc[test_df["userId"] == user_id, "movieId"]) & set(hybrid_score.index)
        for mid in test_movie_ids:
            actual = float(test_df.loc[(test_df["userId"] == user_id) & (test_df["movieId"] == mid), "rating"].iloc[0])
            predicted_scaled = 1 + 4 * float(hybrid_score.loc[mid])
            y_true_scaled.append(actual)
            y_pred_scaled.append(predicted_scaled)

    rmse = calculate_rmse(y_true_scaled, y_pred_scaled) if y_true_scaled else float("nan")
    mae = calculate_mae(y_true_scaled, y_pred_scaled) if y_true_scaled else float("nan")

    result = {
        "rmse": round(rmse, 4) if y_true_scaled else NOT_APPLICABLE,
        "mae": round(mae, 4) if y_true_scaled else NOT_APPLICABLE,
    }
    for key, values in metrics.items():
        result[key] = round(float(np.mean(values)), 4) if values else NOT_APPLICABLE
    result["n_eval_users"] = len(users)
    return result


def build_comparison_table(metrics: dict) -> pd.DataFrame:
    """Build the Model | RMSE | MAE | Precision@5 | Recall@5 comparison table."""
    rows = []
    for model_name, m in metrics.items():
        rows.append({
            "Model": model_name,
            "RMSE": m.get("rmse", NOT_APPLICABLE),
            "MAE": m.get("mae", NOT_APPLICABLE),
            "Precision@5": m.get("precision_at_5", NOT_APPLICABLE),
            "Recall@5": m.get("recall_at_5", NOT_APPLICABLE),
            "Precision@10": m.get("precision_at_10", NOT_APPLICABLE),
            "Recall@10": m.get("recall_at_10", NOT_APPLICABLE),
        })
    return pd.DataFrame(rows)


def save_metrics(metrics: dict, path=config.METRICS_JSON_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Saved metrics to %s", path)


def save_comparison_table(df: pd.DataFrame, path=config.MODEL_COMPARISON_CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved model comparison table to %s", path)
