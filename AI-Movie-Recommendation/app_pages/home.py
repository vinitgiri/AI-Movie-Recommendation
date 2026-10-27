"""
app_pages/home.py
-----------------
CineAI Home Page — Cinematic Hero Section, Featured Movies,
Interactive Genre Explorer, Dataset Stats, and AI Architecture Overview.
"""

from __future__ import annotations

import streamlit as st

from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer
from src.components.model_loader import load_models, load_metrics, models_missing_error
from src.components.movie_card import (
    render_movie_card_with_actions,
    strip_year,
    extract_year,
)
from src.tmdb import get_enriched_movie

inject_global_css()
render_navbar("Home")

# ── Load models ───────────────────────────────────────────────────────────────
movies, ratings, users, hybrid_model, collab_model, missing = load_models()

if missing:
    models_missing_error(missing)
    st.stop()

# ── Hero Section ──────────────────────────────────────────────────────────────
FEATURED_CANDIDATES = [
    "The Godfather (1972)",
    "The Shawshank Redemption (1994)",
    "Pulp Fiction (1994)",
    "The Matrix (1999)",
    "Inception (2010)",
    "Fight Club (1999)",
    "Forrest Gump (1994)",
    "Star Wars: Episode IV - A New Hope (1977)",
]

featured_title = None
featured_row = None
for candidate in FEATURED_CANDIDATES:
    match = movies[movies["title"] == candidate]
    if not match.empty:
        featured_title = candidate
        featured_row = match.iloc[0]
        break

if featured_title is None and not movies.empty:
    featured_row = movies.iloc[0]
    featured_title = featured_row["title"]

# TMDB backdrop
hero_backdrop = None
hero_rating = 8.7
hero_overview = "Spanning decades, the chronicling of a dynasty where loyalty, crime, and legacy collide in one of cinema's greatest masterworks."

if featured_title:
    try:
        enriched = get_enriched_movie(featured_title)
        hero_backdrop = enriched.get("backdrop_url")
        if enriched.get("tmdb_rating"):
            hero_rating = enriched.get("tmdb_rating")
        if enriched.get("overview"):
            hero_overview = enriched.get("overview")
    except Exception:
        pass

featured_clean = strip_year(featured_title) if featured_title else "The Godfather"
featured_year = extract_year(featured_title) if featured_title else "1972"
raw_genres = featured_row.get("genres", "Crime|Drama") if featured_row is not None else "Crime|Drama"
featured_genres_formatted = " • ".join(raw_genres.replace("|", " ").split()[:3])

bg_layer_style = f'background-image: url("{hero_backdrop}");' if hero_backdrop else 'background: radial-gradient(circle at 70% 30%, #2a0808 0%, #0d0d0d 70%);'

# Render Hero Banner HTML
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-bg-layer" style="{bg_layer_style}"></div>
    <div class="hero-gradient-overlay"></div>
    <div class="hero-body">
        <div class="hero-badge">● AI-POWERED RECOMMENDATION ENGINE</div>
        <div class="hero-heading">
            Find Your Next<br><span class="red-accent">Favorite Movie.</span>
        </div>
        <div class="hero-details-meta">
            <span class="star">★ {hero_rating:.1f}</span>
            <span>•</span>
            <span>{featured_year}</span>
            <span>•</span>
            <span>{featured_genres_formatted}</span>
        </div>
        <div class="hero-desc">
            Discover movies tailored specifically to your taste using TF-IDF Content Similarity 
            and SVD Collaborative Matrix Factorization.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Call to Action Buttons
cta_c1, cta_c2, _ = st.columns([1.8, 1.8, 4], gap="medium")
with cta_c1:
    if st.button("⚡ GET MY RECOMMENDATIONS", key="hero_rec_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Recommendations"
        st.rerun()

with cta_c2:
    if st.button("🔍 EXPLORE CATALOG", key="hero_exp_btn", type="secondary", use_container_width=True):
        st.session_state["page"] = "Search"
        st.rerun()

st.markdown("<div style='margin-bottom: 2.8rem;'></div>", unsafe_allow_html=True)

# ── Dataset Stats Counter ─────────────────────────────────────────────────────
metrics = load_metrics()
stats = metrics.get("dataset_stats") if metrics else None

if stats:
    n_movies = f"{stats['n_movies']:,}"
    n_users = f"{stats['n_users']:,}"
    n_ratings = f"{stats['n_ratings']:,}"
    avg_rating = f"{stats['avg_rating']:.2f}"
else:
    n_movies = f"{movies['movieId'].nunique():,}" if not movies.empty else "3,883"
    n_users = f"{ratings['userId'].nunique():,}" if not ratings.empty else "6,040"
    n_ratings = f"{len(ratings):,}" if not ratings.empty else "1,000,209"
    avg_rating = f"{ratings['rating'].mean():.2f}" if not ratings.empty else "3.58"

s1, s2, s3, s4 = st.columns(4, gap="medium")
with s1:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{n_movies}</span>
        <span class="stat-card-tag">Curated Movies</span>
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{n_users}</span>
        <span class="stat-card-tag">User Profiles</span>
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{n_ratings}</span>
        <span class="stat-card-tag">Real Ratings</span>
    </div>""", unsafe_allow_html=True)
with s4:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{avg_rating}★</span>
        <span class="stat-card-tag">Average Rating</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ── Featured Masterpieces / Top Picks ─────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">TOP PICKS</div>
<div class="section-headline">Featured Masterpieces</div>
<div class="section-subheadline">Highly rated landmark films from the MovieLens 1M dataset.</div>
""", unsafe_allow_html=True)

TOP_CURATED_TITLES = [
    "The Godfather (1972)",
    "The Shawshank Redemption (1994)",
    "Pulp Fiction (1994)",
    "Schindler's List (1993)",
    "The Matrix (1999)",
]

top_cols = st.columns(5, gap="small")
for i, title_name in enumerate(TOP_CURATED_TITLES):
    match = movies[movies["title"] == title_name]
    row = match.iloc[0] if not match.empty else {"title": title_name, "genres": "Drama"}
    with top_cols[i]:
        render_movie_card_with_actions(
            row_or_title=row,
            idx_key=f"home_feat_{i}",
            rank=i + 1,
            hybrid_score=0.98 - (i * 0.02),
        )

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ── Explore Genres ────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">BROWSE CATALOG</div>
<div class="section-headline">Explore by Genre</div>
<div class="section-subheadline">Select any genre to dive straight into filtered recommendations.</div>
""", unsafe_allow_html=True)

GENRES = [
    ("Action", "💥"),
    ("Adventure", "🗺️"),
    ("Animation", "🎨"),
    ("Comedy", "😂"),
    ("Crime", "🕵️"),
    ("Drama", "🎭"),
    ("Fantasy", "🧙"),
    ("Horror", "👻"),
    ("Romance", "❤️"),
    ("Sci-Fi", "🚀"),
    ("Thriller", "⚡"),
    ("War", "⚔️"),
]

genre_cols = st.columns(6, gap="small")
for i, (g_name, g_icon) in enumerate(GENRES):
    with genre_cols[i % 6]:
        if st.button(f"{g_icon} {g_name}", key=f"home_genre_{g_name}", use_container_width=True):
            st.session_state["search_genre_filter"] = g_name
            st.session_state["page"] = "Search"
            st.rerun()

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ── How the AI Works ──────────────────────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">HYBRID INTELLIGENCE</div>
<div class="section-headline">How the AI Engine Works</div>
<div class="section-subheadline">An ensemble of content vectorization and latent factor matrix factorization.</div>
""", unsafe_allow_html=True)

arch_col1, arch_col2, arch_col3 = st.columns(3, gap="medium")

with arch_col1:
    st.markdown("""
    <div style="background:#141414;border:1px solid rgba(229,9,20,0.25);border-radius:12px;padding:1.4rem;height:100%;">
        <div style="font-size:0.7rem;font-weight:800;letter-spacing:2px;color:#E50914;margin-bottom:1rem;">
            1. CONTENT-BASED FILTERING
        </div>
        <div class="arch-step-box active-red">Movie Metadata & Genres</div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box">TF-IDF Feature Vectors</div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box active-red">Cosine Similarity Matrix</div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box">Content Score (α)</div>
        <div style="font-size:0.78rem;color:#8A8A8A;margin-top:1rem;line-height:1.5;">
            Calculates pairwise geometric similarity between movie content profiles. Fast, explainable, and zero cold-start latency.
        </div>
    </div>
    """, unsafe_allow_html=True)

with arch_col2:
    st.markdown("""
    <div style="background:#141414;border:1px solid rgba(88,166,255,0.25);border-radius:12px;padding:1.4rem;height:100%;">
        <div style="font-size:0.7rem;font-weight:800;letter-spacing:2px;color:#58A6FF;margin-bottom:1rem;">
            2. COLLABORATIVE SVD
        </div>
        <div class="arch-step-box active-blue">1,000,209 User Ratings</div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box">User–Item Rating Matrix</div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box active-blue">SVD (100 Latent Factors)</div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box">Predicted Rating Score (β)</div>
        <div style="font-size:0.78rem;color:#8A8A8A;margin-top:1rem;line-height:1.5;">
            Discovers hidden taste profiles across 6,040 users by factorizing the rating matrix into low-rank latent spaces.
        </div>
    </div>
    """, unsafe_allow_html=True)

with arch_col3:
    st.markdown("""
    <div style="background:#141414;border:1px solid rgba(63,185,80,0.25);border-radius:12px;padding:1.4rem;height:100%;">
        <div style="font-size:0.7rem;font-weight:800;letter-spacing:2px;color:#3FB950;margin-bottom:1rem;">
            3. WEIGHTED HYBRID FUSION
        </div>
        <div class="arch-step-box" style="border-color:rgba(63,185,80,0.4);background:rgba(63,185,80,0.08);color:#3FB950;">
            Normalize(Scores) → [0, 1]
        </div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box" style="color:#FFF;font-weight:700;">
            Score = α · Content + β · Collab
        </div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box" style="border-color:rgba(63,185,80,0.4);color:#3FB950;">
            Automatic Cold-Start Fallback
        </div>
        <div class="arch-arrow-down">↓</div>
        <div class="arch-step-box" style="background:#1c1c1c;color:#FFF;">
            Ranked Top-N Recommendations
        </div>
        <div style="font-size:0.78rem;color:#8A8A8A;margin-top:1rem;line-height:1.5;">
            Normalizes disparate scales and applies dynamic weighting. Unlocks both serendipity and deep personalization.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

render_footer()
