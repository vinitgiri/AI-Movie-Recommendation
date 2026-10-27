"""
train.py
--------
End-to-end training pipeline:

    check dataset -> load -> preprocess -> train content-based model
    -> train collaborative model -> evaluate all three models
    -> save models -> save metrics -> save comparison table -> save plots

Run with:
    python train.py
"""

from __future__ import annotations

import sys
import time

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split as sk_train_test_split

from src import config, evaluation
from src.collaborative import CollaborativeRecommender
from src.content_based import ContentBasedRecommender
from src.hybrid import HybridRecommender
from src.preprocessing import DatasetNotFoundError, run_preprocessing_pipeline
from src.utils import get_logger

logger = get_logger("train")

sns.set_theme(style="whitegrid")


def _stage(msg: str) -> None:
    """Print a clearly visible stage header."""
    logger.info("")
    logger.info("-" * 60)
    logger.info("  %s", msg)
    logger.info("-" * 60)


def make_plots(movies: pd.DataFrame, ratings: pd.DataFrame, comparison_df: pd.DataFrame) -> None:
    """Generate and save the required visualizations under results/plots/."""
    config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Rating distribution
    plt.figure(figsize=(7, 5))
    rating_counts = ratings["rating"].value_counts().sort_index()
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette="viridis")
    plt.title("Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "rating_distribution.png", dpi=150)
    plt.close()

    # 2. Number of ratings per movie
    per_movie = ratings.groupby("movieId").size()
    plt.figure(figsize=(7, 5))
    sns.histplot(per_movie, bins=50, log_scale=(False, True), color="#4c72b0")
    plt.title("Number of Ratings per Movie")
    plt.xlabel("Ratings per Movie")
    plt.ylabel("Count of Movies (log scale)")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "ratings_per_movie.png", dpi=150)
    plt.close()

    # 3. Number of ratings per user
    per_user = ratings.groupby("userId").size()
    plt.figure(figsize=(7, 5))
    sns.histplot(per_user, bins=50, log_scale=(False, True), color="#55a868")
    plt.title("Number of Ratings per User")
    plt.xlabel("Ratings per User")
    plt.ylabel("Count of Users (log scale)")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "ratings_per_user.png", dpi=150)
    plt.close()

    # 4. Top-rated movies (by mean rating, min 20 ratings for reliability)
    movie_stats = ratings.groupby("movieId")["rating"].agg(["mean", "count"])
    movie_stats = movie_stats[movie_stats["count"] >= 20].sort_values("mean", ascending=False).head(15)
    movie_titles = movies.set_index("movieId").loc[movie_stats.index, "title"]
    plt.figure(figsize=(8, 6))
    sns.barplot(x=movie_stats["mean"].values, y=movie_titles.values, orient="h", palette="magma")
    plt.title("Top-Rated Movies (min. 20 ratings)")
    plt.xlabel("Average Rating")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "top_rated_movies.png", dpi=150)
    plt.close()

    # 5. Model comparison (RMSE/MAE where numeric)
    numeric_cmp = comparison_df.copy()
    for col in ["RMSE", "MAE"]:
        numeric_cmp[col] = pd.to_numeric(numeric_cmp[col], errors="coerce")
    plt.figure(figsize=(7, 5))
    melted = numeric_cmp.melt(id_vars="Model", value_vars=["RMSE", "MAE"], var_name="Metric", value_name="Value")
    sns.barplot(data=melted, x="Model", y="Value", hue="Metric", palette="Set2")
    plt.title("Model Comparison — RMSE / MAE (lower is better)")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "model_comparison.png", dpi=150)
    plt.close()

    # 6. Precision@K comparison
    plt.figure(figsize=(7, 5))
    prec_cmp = comparison_df.copy()
    for col in ["Precision@5", "Precision@10"]:
        prec_cmp[col] = pd.to_numeric(prec_cmp[col], errors="coerce")
    melted = prec_cmp.melt(id_vars="Model", value_vars=["Precision@5", "Precision@10"], var_name="K", value_name="Precision")
    sns.barplot(data=melted, x="Model", y="Precision", hue="K", palette="coolwarm")
    plt.title("Precision@K Comparison")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "precision_at_k_comparison.png", dpi=150)
    plt.close()

    # 7. Recall@K comparison
    plt.figure(figsize=(7, 5))
    rec_cmp = comparison_df.copy()
    for col in ["Recall@5", "Recall@10"]:
        rec_cmp[col] = pd.to_numeric(rec_cmp[col], errors="coerce")
    melted = rec_cmp.melt(id_vars="Model", value_vars=["Recall@5", "Recall@10"], var_name="K", value_name="Recall")
    sns.barplot(data=melted, x="Model", y="Recall", hue="K", palette="coolwarm")
    plt.title("Recall@K Comparison")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "recall_at_k_comparison.png", dpi=150)
    plt.close()

    logger.info("Saved 7 plots to %s", config.PLOTS_DIR)


def main() -> int:
    start = time.time()
    logger.info("=" * 70)
    logger.info("AI-Based Personalized Movie Recommendation System -- Training")
    logger.info("=" * 70)

    # ── Stage 1-3: Check, load, preprocess ────────────────────────────────
    _stage("Stage 1/10: Checking dataset, loading, and preprocessing")
    try:
        movies, ratings, users, stats = run_preprocessing_pipeline()
    except DatasetNotFoundError as e:
        logger.error(str(e))
        return 1

    logger.info(
        "Dataset stats: %d movies | %d users | %d ratings | avg rating %.3f",
        stats.n_movies, stats.n_users, stats.n_ratings, stats.avg_rating,
    )

    # Train/test split (user-item level) for content-based & hybrid evaluation
    _stage("Stage 2/10: Creating train/test split")
    train_df, test_df = sk_train_test_split(
        ratings, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED
    )
    logger.info("Train: %d ratings | Test: %d ratings", len(train_df), len(test_df))

    # ── Stage 4: Train content-based model ────────────────────────────────
    _stage("Stage 3/10: Training Content-Based model (TF-IDF + Cosine Similarity)")
    content_model = ContentBasedRecommender(movies).fit()

    # ── Stage 5: Train collaborative SVD model ────────────────────────────
    _stage("Stage 4/10: Training Collaborative Filtering model (SVD — evaluation split)")
    collab_eval_model = CollaborativeRecommender(train_df, movies).fit(full_fit=False)

    _stage("Stage 5/10: Training Collaborative Filtering model (SVD — production, full data)")
    collab_prod_model = CollaborativeRecommender(ratings, movies).fit(full_fit=True)

    # ── Stage 6: Evaluate all three models ────────────────────────────────
    _stage("Stage 6/10: Evaluating models (up to %d sample users)" % evaluation.MAX_EVAL_USERS)
    content_metrics = evaluation.evaluate_content_based(content_model, train_df, test_df, config.TOP_K_VALUES)
    logger.info("  Content-Based evaluation complete.")
    collab_metrics = evaluation.evaluate_collaborative(collab_eval_model, train_df, test_df, config.TOP_K_VALUES)
    logger.info("  Collaborative evaluation complete.")
    hybrid_metrics = evaluation.evaluate_hybrid(
        content_model, collab_eval_model, train_df, test_df, config.TOP_K_VALUES
    )
    logger.info("  Hybrid evaluation complete.")

    all_metrics = {
        "dataset_stats": stats.to_dict(),
        "Content-Based": content_metrics,
        "Collaborative": collab_metrics,
        "Hybrid": hybrid_metrics,
    }

    # ── Stage 7: Save models ──────────────────────────────────────────────
    _stage("Stage 7/10: Saving trained models")
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(content_model.tfidf_vectorizer, config.TFIDF_VECTORIZER_PATH)
    joblib.dump(content_model.tfidf_matrix, config.TFIDF_MATRIX_PATH)
    joblib.dump(content_model.similarity_matrix, config.COSINE_SIM_PATH)
    joblib.dump(collab_prod_model.model, config.SVD_MODEL_PATH)
    joblib.dump(movies, config.MOVIES_CLEAN_PATH)
    joblib.dump(ratings, config.RATINGS_CLEAN_PATH)
    joblib.dump(users, config.USERS_CLEAN_PATH)
    logger.info("Saved all models and data to %s", config.MODELS_DIR)

    # ── Stage 8: Save metrics ─────────────────────────────────────────────
    _stage("Stage 8/10: Saving evaluation metrics")
    evaluation.save_metrics(all_metrics)

    # ── Stage 9: Generate comparison results ──────────────────────────────
    _stage("Stage 9/10: Generating comparison table")
    comparison_df = evaluation.build_comparison_table(
        {"Content-Based": content_metrics, "Collaborative": collab_metrics, "Hybrid": hybrid_metrics}
    )
    evaluation.save_comparison_table(comparison_df)

    # ── Stage 10: Generate plots ──────────────────────────────────────────
    _stage("Stage 10/10: Generating visualization plots")
    make_plots(movies, ratings, comparison_df)

    # ── Training summary ──────────────────────────────────────────────────
    elapsed = time.time() - start
    logger.info("")
    logger.info("=" * 70)
    logger.info("  TRAINING SUMMARY")
    logger.info("=" * 70)
    logger.info("Movies: %d | Users: %d | Ratings: %d", stats.n_movies, stats.n_users, stats.n_ratings)
    logger.info("Average Rating: %.3f", stats.avg_rating)
    logger.info("")
    logger.info("Model Comparison:")
    logger.info("\n%s", comparison_df.to_string(index=False))
    logger.info("")
    logger.info("Elapsed time: %.1f seconds", elapsed)
    logger.info("Models saved to: %s", config.MODELS_DIR)
    logger.info("Metrics saved to: %s", config.METRICS_JSON_PATH)
    logger.info("Comparison table saved to: %s", config.MODEL_COMPARISON_CSV_PATH)
    logger.info("Plots saved to: %s", config.PLOTS_DIR)
    logger.info("")
    logger.info("Training complete. Run 'streamlit run app.py' to launch the application.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
