# AI-Based Personalized Movie Recommendation System Using Hybrid Filtering Techniques

A B.Tech (Information Technology) academic project that builds a working, end-to-end
movie recommendation engine on the MovieLens 1M dataset, combining **Content-Based
Filtering** (TF-IDF + cosine similarity over genres) with **Collaborative Filtering**
(SVD via `scikit-surprise`) through a **configurable weighted hybrid model**, served
through a Streamlit web application.

Every recommendation is generated from the real dataset and trained models — nothing
is hardcoded or random.

---

## 1. Project Overview

Recommendation systems help users navigate large content catalogs by predicting what
they are likely to enjoy. This project demonstrates the two classical families of
approaches — content-based and collaborative filtering — and shows how combining them
in a hybrid model addresses each approach's individual weaknesses (cold start for
collaborative filtering, lack of personalization for content-based filtering).

### Problem Statement
Single-strategy recommenders have known weaknesses: collaborative filtering cannot
recommend to new users or new items (cold start), while content-based filtering
cannot capture the "taste" signal hidden in collective rating behavior. This project
builds a hybrid system that draws on both signals and degrades gracefully when one is
unavailable.

### Objectives
- Build a real, working recommender on the MovieLens 1M dataset — no fabricated output.
- Implement content-based filtering (TF-IDF + cosine similarity) and collaborative
  filtering (SVD) as independent, testable modules.
- Combine both into a hybrid model with configurable, normalized weighting.
- Evaluate all three models with a shared, honest evaluation framework (RMSE, MAE,
  Precision@K, Recall@K).
- Serve recommendations through an interactive Streamlit interface.

---

## 2. System Architecture

```
MovieLens Dataset
        |
Data Preprocessing
        |
 +-------------------+-----------------------+
 |                                            |
 v                                            v
Content-Based Filtering                Collaborative Filtering
 |                                            |
TF-IDF                                       SVD
 |                                            |
Cosine Similarity                     Predicted Ratings
 +-------------------+-----------------------+
                      |
              Score Normalization
                      |
              Weighted Hybrid Model
                      |
              Recommendation Ranking
                      |
                  Top-N Movies
                      |
              Streamlit Web Interface
```

---

## 3. Features

- **Content-based filtering** — genre TF-IDF vectors + cosine similarity for
  movie-to-movie recommendations.
- **Collaborative filtering** — SVD matrix factorization trained on real user ratings,
  80:20 train/test split with a fixed random seed.
- **Hybrid model** — `hybrid_score = α · normalized_content_score + β · normalized_collaborative_score`,
  with α + β = 1, adjustable live from the sidebar.
- **Personalization** — recommend for a specific User ID, or find movies similar to a
  chosen title.
- **Cold-start handling** — users with too little rating history automatically fall
  back to content-based recommendations, clearly flagged in the UI.
- **Evaluation framework** — RMSE, MAE, Precision@K, Recall@K, computed identically
  across all three models, with "N/A" shown instead of invented numbers where a metric
  doesn't apply.
- **Explainability** — every recommendation includes a plain-language reason.
- **Caching** — models train once (`train.py`) and are loaded, not retrained, by the
  Streamlit app.

---

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Data | Pandas, NumPy |
| ML | Scikit-learn, SciPy, Scikit-Surprise |
| Persistence | Joblib |
| Web UI | Streamlit |
| Visualization | Matplotlib, Seaborn |
| Testing | Pytest |

---

## 5. Dataset

This project uses the **MovieLens 1M** dataset from GroupLens Research
(https://grouplens.org/datasets/movielens/1m/): ~1,000,209 ratings from 6,040 users on
~3,900 movies.

The dataset is **not included in this repository** (see `.gitignore`) — GroupLens's
license does not permit redistribution. Download it yourself and place the three
`.dat` files here:

```
data/ml-1m/
    movies.dat
    ratings.dat
    users.dat
```

`movies.dat` — `movieId::title::genres` (genres are `|`-separated, e.g. `Animation|Children's|Comedy`)
`ratings.dat` — `userId::movieId::rating::timestamp`
`users.dat` — `userId::gender::age::occupation::zipCode`

The pipeline reads the `::` delimiter directly with `pandas.read_csv(..., sep="::", engine="python")`.

> **Note on this repository's development history:** because the sandboxed environment
> this project was built in cannot reach `grouplens.org`, the pipeline (`train.py`,
> `app.py`, and the full test suite) was verified end-to-end against a small
> synthetically generated dataset in the exact ml-1m format (same delimiter, same
> column layout, same value ranges). That fixture is not part of this deliverable —
> download the real MovieLens 1M dataset per the instructions above before running
> `train.py` for actual coursework results.

---

## 6. Project Structure

```
AI-Movie-Recommendation/
├── data/ml-1m/                  # place movies.dat, ratings.dat, users.dat here
├── models/                      # trained models (generated by train.py)
├── src/
│   ├── config.py                # all paths, hyperparameters, seeds
│   ├── preprocessing.py         # load, validate, clean, compute stats
│   ├── content_based.py         # TF-IDF + cosine similarity
│   ├── collaborative.py         # SVD collaborative filtering
│   ├── hybrid.py                # weighted hybrid model + cold-start fallback
│   ├── evaluation.py            # RMSE, MAE, Precision@K, Recall@K
│   └── utils.py                 # logging, normalization helpers
├── notebooks/exploratory_analysis.ipynb
├── results/                     # metrics.json, model_comparison.csv, plots/
├── tests/                       # pytest suite (29 tests)
├── app.py                       # Streamlit application
├── train.py                     # end-to-end training pipeline
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## 7. Installation

```bash
git clone <your-repo-url>
cd AI-Movie-Recommendation

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Dataset Setup
1. Download `ml-1m.zip` from https://grouplens.org/datasets/movielens/1m/
2. Extract it and copy `movies.dat`, `ratings.dat`, `users.dat` into `data/ml-1m/`

---

## 8. Training

```bash
python train.py
```

This performs, in order: dataset check → load → preprocess → train content-based
model → train collaborative SVD model → evaluate all three models → save models to
`models/` → save `results/metrics.json` and `results/model_comparison.csv` → generate
7 plots in `results/plots/` → print a training summary.

---

## 9. Running the Application

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. The app loads the models saved by `train.py` — it
never retrains on a page refresh. If `models/` is empty, the app shows a clear message
telling you to run `train.py` first.

---

## 10. Evaluation

Metrics are computed on an 80:20 train/test split (fixed seed = 42) and saved to
`results/metrics.json` / `results/model_comparison.csv`:

| Model | RMSE | MAE | Precision@5 | Recall@5 |
|---|---|---|---|---|
| Content-Based | N/A | N/A | ✅ | ✅ |
| Collaborative | ✅ | ✅ | ✅ | ✅ |
| Hybrid | ✅* | ✅* | ✅ | ✅ |

RMSE/MAE are not meaningful for pure content-based ranking (it produces similarity
scores, not 1–5 rating predictions), so those cells are reported as `N/A` rather than
invented. \*The hybrid model's RMSE/MAE are computed by rescaling its normalized
[0, 1] hybrid score back onto the 1–5 rating scale — a reasonable approximation,
documented in `src/evaluation.py`, not an exact rating prediction.

A relevance threshold of `rating >= 4.0` is used for Precision@K / Recall@K, evaluated
at K = 5 and K = 10 over a sample of up to 300 test users for speed on the full 1M
dataset.

**Actual numbers depend on your run of the real dataset** — see
`results/metrics.json` and `results/model_comparison.csv` after running `train.py`.
No results are fabricated or hardcoded in this repository.

---

## 11. Results

Run `python train.py` to populate:
- `results/metrics.json` — full metric breakdown per model
- `results/model_comparison.csv` — the comparison table above, with real numbers
- `results/plots/` — rating distribution, ratings-per-movie, ratings-per-user,
  top-rated movies, model comparison, Precision@K comparison, Recall@K comparison

## 12. Screenshots

_Add screenshots of the running Streamlit app here after your first `streamlit run app.py` session._

---

## 13. How the Models Work

### Content-Based Filtering
Each movie's `|`-separated genre string (e.g. `Animation|Children's|Comedy`) is
converted to space-separated text and vectorized with `TfidfVectorizer`. Cosine
similarity between every pair of TF-IDF vectors produces a movie-to-movie similarity
matrix. "Similar movies" recommendations are the nearest neighbors of a selected
title; for a known user, a content affinity score for every movie is the mean
similarity to the movies that user rated ≥ 4.0.

### Collaborative Filtering
User ratings are loaded into `scikit-surprise`'s `SVD`, a matrix-factorization model
that learns latent factors for users and movies from the observed rating matrix and
predicts ratings for unseen (user, movie) pairs. Trained on an 80:20 split (seed = 42)
for evaluation, and separately refit on 100% of the data for the production model that
actually generates recommendations.

### Hybrid Filtering
Content scores (cosine similarity, roughly [0, 1] already) and collaborative scores
(predicted ratings, [1, 5]) live on different scales, so each is min-max normalized to
[0, 1] independently before combining:

```
hybrid_score = content_weight * normalized_content_score
             + collaborative_weight * normalized_collaborative_score
```

with `content_weight + collaborative_weight = 1` (default 0.5 / 0.5, adjustable in the
Streamlit sidebar). Already-rated and duplicate movies are removed before ranking.

---

## 14. Known Limitations

- Content-based signal is genre-only (MovieLens 1M has no plot, cast, or tag data),
  so it cannot distinguish two movies that share genres but differ heavily in tone,
  quality, or era.
- SVD collaborative filtering, like all matrix-factorization methods, struggles for
  users/movies with very few ratings — this project's cold-start fallback addresses
  users, not brand-new movies with zero ratings.
- The hybrid model's RMSE/MAE are an approximation (see Section 10), not a true rating
  prediction, since the hybrid score is a ranking score rather than a calibrated
  1–5 estimate.
- Evaluation samples up to 300 users for Precision@K/Recall@K for runtime reasons on
  the 1M-row dataset; this is a reasonable but not exhaustive sample.

## 15. Future Scope

- Enrich content-based features with plot synopses/tags via NLP embeddings
  (e.g. MovieLens's `tag.csv` in newer dataset versions, or an external metadata API).
- Replace linear hybrid weighting with a learned meta-model (e.g. a small
  gradient-boosted ranker) that combines content and collaborative signals.
- Add implicit-feedback signals (watch time, clicks) alongside explicit ratings.
- Support the larger MovieLens 20M/25M datasets for more robust evaluation.
- Add user authentication and persistent rating collection for continuous learning.

## 16. References

1. F. Maxwell Harper and Joseph A. Konstan. 2015. *The MovieLens Datasets: History and
   Context.* ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4, Article 19.
2. Koren, Y., Bell, R., & Volinsky, C. (2009). *Matrix Factorization Techniques for
   Recommender Systems.* IEEE Computer, 42(8), 30–37.
3. Ricci, F., Rokach, L., & Shapira, B. (2015). *Recommender Systems Handbook* (2nd ed.).
   Springer.
4. Scikit-learn documentation — `TfidfVectorizer`, `cosine_similarity`.
5. Scikit-Surprise documentation — `SVD`.
6. Streamlit documentation.

---

## License

MIT License for the source code in this repository — see `LICENSE`. The MovieLens
dataset itself is distributed separately by GroupLens Research under its own terms.
