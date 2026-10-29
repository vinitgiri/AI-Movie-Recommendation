# 🎬 AI-Based Personalized Movie Recommendation System

An intelligent movie recommendation system that combines **Content-Based Filtering** and **Collaborative Filtering** to provide personalized movie recommendations using Machine Learning.

## 📌 About the Project

The AI-Based Personalized Movie Recommendation System helps users discover movies based on their interests, preferences, and rating patterns. It uses a hybrid recommendation approach to combine movie-content similarity with collaborative user preferences.

The project integrates the MovieLens dataset with TMDB API to display movie posters and additional movie information, creating an interactive movie discovery experience.

## ✨ Features

- 🎯 **Personalized Recommendations** — Discover movies based on user preferences.
- 🧠 **Content-Based Filtering** — Uses TF-IDF and cosine similarity to identify similar movies.
- 👥 **Collaborative Filtering** — Uses Singular Value Decomposition (SVD) to estimate user preferences.
- 🔀 **Hybrid Recommendation Engine** — Combines content-based and collaborative scores.
- 🎞️ **Movie Posters & Metadata** — Uses TMDB API for movie images and additional information.
- 🔍 **Movie Discovery** — Browse and explore available movies.
- 📊 **Model Evaluation** — Supports metrics such as RMSE, MAE, Precision@K and Recall@K.
- 🖥️ **Interactive Web Interface** — Built with Streamlit.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas & NumPy | Data processing |
| Scikit-learn | TF-IDF and cosine similarity |
| Surprise / SVD implementation | Collaborative filtering, depending on the configured backend |
| MovieLens | Movie ratings and metadata dataset |
| TMDB API | Movie posters and metadata |
| Pickle | Saving trained models and processed data |

## ⚙️ Recommendation Workflow

1. Load movie information and user ratings from the MovieLens dataset.
2. Preprocess movie metadata and rating data.
3. Build a content-based model using TF-IDF and cosine similarity.
4. Train or load the collaborative filtering model using SVD.
5. Normalize and combine recommendation scores using a weighted hybrid approach.
6. Rank movies and generate Top-N recommendations.
7. Display movie recommendations through the Streamlit interface.

### Hybrid Recommendation Formula

\[
S_{\text{hybrid}}(u,i)=
\alpha S_{\text{content}}(u,i)+
(1-\alpha)S_{\text{collaborative}}(u,i)
\]

Here, \(\alpha\) controls the relative contribution of content-based and collaborative filtering. The scores should be appropriately normalized, and the weight can be tuned experimentally.

## 📂 Project Structure

```text
AI-Movie-Recommendation/
├── app.py
├── app_pages/
├── src/
│   ├── components/
│   ├── ui/
│   ├── config.py
│   ├── preprocessing.py
│   ├── content_based.py
│   ├── collaborative.py
│   ├── hybrid.py
│   ├── evaluation.py
│   ├── tmdb.py
│   └── utils.py
├── data/
│   └── ml-1m/
├── models/
├── notebooks/
├── results/
├── tests/
├── .streamlit/
├── requirements.txt
├── .gitignore
└── README.md
```

*Note: The exact files and folders may differ depending on your local project version.*

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vinitgiri/AI-Movie-Recommendation.git
cd AI-Movie-Recommendation
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure TMDB API

Create or update `.streamlit/secrets.toml`:

```toml
[tmdb]
api_key = "YOUR_TMDB_API_KEY"
```

Replace `YOUR_TMDB_API_KEY` with your own TMDB API key. Never commit this file or expose your API key publicly.

If TMDB configuration is optional in your current setup, the application may still run without movie images or additional metadata.

### 5. Run the Application

```bash
python -m streamlit run app.py

Open the local URL shown in the terminal, usually:

**http://localhost:8501**

## 📊 Model Evaluation

The system can be evaluated using the following metrics:

- **RMSE:** Measures the root mean squared prediction error.
- **MAE:** Measures the average absolute prediction error.
- **Precision@K:** Measures the proportion of relevant movies in the top K recommendations.
- **Recall@K:** Measures the proportion of relevant movies successfully recommended.

Actual performance values should be added after running the evaluation on your chosen train-test split.

## 🎯 Project Objectives

- Develop a personalized movie recommendation system.
- Compare content-based and collaborative filtering approaches.
- Combine both approaches using a hybrid recommendation strategy.
- Improve movie discovery through an interactive interface.
- Evaluate recommendation quality using standard machine-learning metrics.

## 🔮 Future Enhancements

- User login and personalized profiles.
- Improved cold-start handling for new users and movies.
- Experimentally optimized hybrid weights.
- More detailed recommendation explanations.
- Enhanced search, filtering, favorites and movie details.
- Deployment as a publicly accessible web application.

## 🎓 Academic Project

**Project Title:** AI-Based Personalized Movie Recommendation System Using Hybrid Filtering Techniques

**Degree:** Bachelor of Technology (B.Tech)

**Department:** Information Technology

**Institution:** Greater Noida Institute of Technology (GNIOT)

## ⚠️ Disclaimer

This project is intended for educational and research purposes. Movie information and images may be provided through TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.

## 👨‍💻 Author

**Vinit Kumar Giri**

- GitHub: [@vinitgiri](https://github.com/vinitgiri)

---

⭐ If you find this project useful, consider giving the repository a star!
