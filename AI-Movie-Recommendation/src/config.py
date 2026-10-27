"""
config.py
---------
Central configuration for the AI-Based Personalized Movie Recommendation
System. All paths, hyperparameters, and reproducibility settings live here
so the rest of the codebase never hardcodes them.
"""

from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "ml-1m"
MOVIES_FILE = DATA_DIR / "movies.dat"
RATINGS_FILE = DATA_DIR / "ratings.dat"
USERS_FILE = DATA_DIR / "users.dat"

MODELS_DIR = BASE_DIR / "models"
TFIDF_VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
TFIDF_MATRIX_PATH = MODELS_DIR / "tfidf_matrix.pkl"
COSINE_SIM_PATH = MODELS_DIR / "cosine_similarity.pkl"
SVD_MODEL_PATH = MODELS_DIR / "svd_model.pkl"
MOVIES_CLEAN_PATH = MODELS_DIR / "movies_clean.pkl"
RATINGS_CLEAN_PATH = MODELS_DIR / "ratings_clean.pkl"
USERS_CLEAN_PATH = MODELS_DIR / "users_clean.pkl"

RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
METRICS_JSON_PATH = RESULTS_DIR / "metrics.json"
MODEL_COMPARISON_CSV_PATH = RESULTS_DIR / "model_comparison.csv"

# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------
RANDOM_SEED = 42

# --------------------------------------------------------------------------
# Data splitting
# --------------------------------------------------------------------------
TEST_SIZE = 0.2

# --------------------------------------------------------------------------
# Collaborative filtering (SVD via scikit-surprise)
# --------------------------------------------------------------------------
SVD_N_FACTORS = 100
SVD_N_EPOCHS = 20
SVD_LR_ALL = 0.005
SVD_REG_ALL = 0.02
RATING_SCALE = (1, 5)

# --------------------------------------------------------------------------
# Hybrid model
# --------------------------------------------------------------------------
DEFAULT_CONTENT_WEIGHT = 0.5
DEFAULT_COLLABORATIVE_WEIGHT = 0.5

# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------
TOP_K_VALUES = [5, 10]
RELEVANCE_THRESHOLD = 4.0  # a rating >= this value is considered "relevant"

# --------------------------------------------------------------------------
# Cold-start handling
# --------------------------------------------------------------------------
MIN_RATINGS_FOR_COLLABORATIVE = 5  # users below this fall back to content-based

# --------------------------------------------------------------------------
# Recommendations
# --------------------------------------------------------------------------
DEFAULT_TOP_N = 10

# --------------------------------------------------------------------------
# UI Constants
# --------------------------------------------------------------------------
FEATURED_TITLES = [
    'Godfather, The (1972)',
    'Matrix, The (1999)',
    'Pulp Fiction (1994)',
    'Shawshank Redemption, The (1994)',
    'Star Wars: Episode V - The Empire Strikes Back (1980)',
    'Gladiator (2000)',
    'Forrest Gump (1994)',
]

# Trending movies for the homepage — all verified to exist in ML-1M dataset.
TRENDING_TITLES = [
    'Silence of the Lambs, The (1991)',
    'American Beauty (1999)',
    'Braveheart (1995)',
    'Fight Club (1999)',
    'Forrest Gump (1994)',
    'Matrix, The (1999)',
    'Pulp Fiction (1994)',
    'Shawshank Redemption, The (1994)',
]