"""
src/ui/home.py
--------------
Cinematic Landing Page / Home View for CineAI.
Matches visual reference:
  - 74vh Hero with high-res TMDB backdrop, left alignment, badge pills, metadata, spotlight preview
  - Compact inline stats strip
  - Trending Now recommendations row (8 movies)
  - 11-genre explorer with circular icon cards
  - Premium footer
"""

from __future__ import annotations

import streamlit as st

from src.config import FEATURED_TITLES, TRENDING_TITLES
from src.tmdb import backdrop_url as tmdb_backdrop_url
from src.tmdb import get_enriched_movie
from src.tmdb import poster_url as tmdb_poster_url
from src.tmdb_catalog import load_tmdb_catalog
from src.ui.components import (
    _extract_year,
    _strip_year,
    render_empty_state,
    render_movie_grid,
    render_section_header,
    render_stat_card,
    spacer,
)
from src.ui.navigation import render_navbar, render_footer
from src.ui.styles import inject_global_css
from src.components.model_loader import load_models, load_metrics, models_missing_error


def render():
    """Render the complete cinematic home page."""
    inject_global_css()
    render_navbar("Home")

    movies, ratings, users, hybrid_model, collab_model, missing = load_models()
    if missing:
        models_missing_error(missing)
        return

    catalog = load_tmdb_catalog()
    if catalog.empty:
        catalog = movies

    # 1. Cinematic Hero Banner
    _render_hero(catalog)

    # 2. Inline Stats Strip
    _render_stats_strip(movies, ratings)

    # 3. Trending / Top Picks
    _render_trending_section(catalog)

    # 4. Explore Genres
    _render_genres_section(movies)

    # 5. Footer
    render_footer()


# ─── HERO SECTION ──────────────────────────────────────────────────────────────

def _render_hero(movies):
    """Render the cinematic hero banner with a looping TMDB-backed carousel."""
    if "hero_carousel_idx" not in st.session_state:
        st.session_state["hero_carousel_idx"] = 0

    if movies is not None and not movies.empty:
        if "tmdb_id" in movies.columns:
            featured_movies = movies.head(8).reset_index(drop=True)
        else:
            featured_movies = movies[movies["title"].isin(FEATURED_TITLES)].reset_index(drop=True)
            if featured_movies.empty:
                featured_movies = movies.head(8).reset_index(drop=True)
    else:
        featured_movies = None

    carousel_size = len(featured_movies) if featured_movies is not None else len(FEATURED_TITLES)
    idx = int(st.session_state.get("hero_carousel_idx", 0)) % carousel_size
    if featured_movies is not None:
        movie_row = featured_movies.iloc[idx]
        featured_title = str(movie_row.get("title", "Featured Movie"))
    else:
        movie_row = {}
        featured_title = FEATURED_TITLES[idx]

    # TMDB enrichment
    tmdb_data = {}
    backdrop_url = None
    try:
        tmdb_data = get_enriched_movie(featured_title) or {}
        backdrop_url = tmdb_data.get("backdrop_url")
    except Exception:
        pass

    if not backdrop_url and hasattr(movie_row, "get"):
        backdrop_url = tmdb_backdrop_url(movie_row.get("backdrop_path"))
    if not backdrop_url and hasattr(movie_row, "get"):
        backdrop_url = tmdb_poster_url(movie_row.get("poster_path"), size="w780")

    bg_css = f"background-image: url('{backdrop_url}');" if backdrop_url else "background: linear-gradient(135deg, #161616 0%, #0d0d0d 100%);"

    year = _extract_year(featured_title)
    short_title = _strip_year(featured_title)
    raw_genres = str(movie_row.get("genres", "")) if hasattr(movie_row, "get") else ""
    genres_str = raw_genres.replace("|", " · ") if raw_genres else "Drama"

    rating_val = tmdb_data.get("tmdb_rating") or (movie_row.get("vote_average") if hasattr(movie_row, "get") else None)
    try:
        rating_num = float(rating_val) if rating_val is not None else 8.8
    except (ValueError, TypeError):
        rating_num = 8.8

    raw_overview = tmdb_data.get("overview") or (movie_row.get("overview") if hasattr(movie_row, "get") else None)
    if raw_overview and isinstance(raw_overview, str) and len(raw_overview.strip()) > 0:
        overview = raw_overview.strip()
    else:
        overview = "An iconic cinematic masterpiece in the MovieLens archive."

    short_overview = (overview[:160] + "...") if len(overview) > 160 else overview

    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-bg-art" style="{bg_css}"></div>
        <div class="hero-overlay-radial"></div>
        <div class="hero-left-content">
            <div class="hero-badge-pill">
                AI-POWERED RECOMMENDATIONS
            </div>
            <div class="hero-main-title">
                Find Your Next<br><span class="red-text">Favorite Movie.</span>
            </div>
            <div class="hero-synopsis">
                Discover movies tailored to your taste using Hybrid Machine Learning
                — Content-Based Filtering and Collaborative Filtering.
            </div>
            <div class="hero-metadata-row">
                <span class="gold-star">★ {rating_num:.1f}</span>
                <span>•</span>
                <span>{year if year else "1994"}</span>
                <span>•</span>
                <span>{genres_str}</span>
            </div>
        </div>
        <div class="hero-right-preview">
            <div class="hero-preview-title">{short_title}</div>
            <div class="hero-preview-meta">
                <span>{year if year else "Classic"}</span>
                <span>·</span>
                <span>{genres_str.split(' · ')[0] if ' · ' in genres_str else genres_str}</span>
                <span>·</span>
                <span style="color:#FFD700;font-weight:700;">★ {rating_num:.1f}/10</span>
            </div>
            <div class="hero-preview-desc">{short_overview}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Action Buttons
    c1, c2, c3, c4 = st.columns([1.6, 1.4, 4.2, 0.8], gap="small")
    with c1:
        if st.button("▶ Get Recommendations →", key="hero_btn_rec", type="primary", use_container_width=True):
            st.session_state["page"] = "Recommendations"
            st.rerun()
    with c2:
        if st.button("🎬 Explore Movies", key="hero_btn_explore", use_container_width=True):
            st.session_state["page"] = "Movies"
            st.rerun()
    with c4:
        col_prev, col_next = st.columns(2, gap="small")
        with col_prev:
            if st.button("❮", key="hero_prev_spotlight", help="Previous featured movie", use_container_width=True):
                st.session_state["hero_carousel_idx"] = (idx - 1) % carousel_size
                st.rerun()
        with col_next:
            if st.button("❯", key="hero_next_spotlight", help="Next featured movie", use_container_width=True):
                st.session_state["hero_carousel_idx"] = (idx + 1) % carousel_size
                st.rerun()


# ─── STATS STRIP ──────────────────────────────────────────────────────────────

def _render_stats_strip(movies, ratings):
    """Render compact inline statistics strip below hero."""
    metrics = load_metrics()
    stats = metrics.get("dataset_stats") if metrics else None

    if stats:
        n_movies = f"{stats['n_movies']:,}"
        n_users = f"{stats['n_users']:,}"
        n_ratings = f"{stats['n_ratings']:,}"
    else:
        n_movies = f"{movies['movieId'].nunique():,}" if not movies.empty else "3,883"
        n_users = f"{ratings['userId'].nunique():,}" if not ratings.empty else "6,040"
        n_ratings = f"{len(ratings):,}" if not ratings.empty else "1,000,209"

    # Shorten ratings display
    try:
        r_num = int(n_ratings.replace(",", ""))
        if r_num >= 1_000_000:
            n_ratings_display = f"{r_num / 1_000_000:.0f}M+"
        elif r_num >= 1_000:
            n_ratings_display = f"{r_num / 1_000:.0f}K+"
        else:
            n_ratings_display = n_ratings
    except (ValueError, AttributeError):
        n_ratings_display = n_ratings

    st.markdown(f"""
    <div class="stats-strip">
        <div class="stat-inline-item">
            <span class="stat-inline-icon">🎬</span>
            <div class="stat-inline-text">
                <span class="stat-inline-number">{n_movies}</span>
                <span class="stat-inline-label">Movies</span>
            </div>
        </div>
        <div class="stat-inline-item">
            <span class="stat-inline-icon">👤</span>
            <div class="stat-inline-text">
                <span class="stat-inline-number">{n_users}</span>
                <span class="stat-inline-label">Users</span>
            </div>
        </div>
        <div class="stat-inline-item">
            <span class="stat-inline-icon">⭐</span>
            <div class="stat-inline-text">
                <span class="stat-inline-number">{n_ratings_display}</span>
                <span class="stat-inline-label">Ratings</span>
            </div>
        </div>
        <div class="stat-inline-item">
            <span class="stat-inline-icon">🤖</span>
            <div class="stat-inline-text">
                <span class="stat-inline-number">AI</span>
                <span class="stat-inline-label">Powered</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── TRENDING SECTION ─────────────────────────────────────────────────────────

def _render_trending_section(movies):
    """Render TRENDING NOW section with curated movie poster cards."""

    # Section header with View All
    st.markdown("""
    <div class="section-header-row">
        <div class="section-header-left">
            <div style="font-size:1.4rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px;">Trending Now</div>
            <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.2rem;">Popular movies recommended for you</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Build list of movies to show — try TRENDING_TITLES first, then fall back
    trending_movies = []
    for title in TRENDING_TITLES:
        if movies is not None and not movies.empty:
            match = movies[movies["title"] == title]
            if not match.empty:
                trending_movies.append(title)

    # If not enough from TRENDING_TITLES, pad with popular movies from dataset
    if len(trending_movies) < 8 and movies is not None and not movies.empty:
        existing_titles = set(trending_movies)
        # Fallback: use first N movies from FEATURED_TITLES not already in list
        for ft in FEATURED_TITLES:
            if ft not in existing_titles:
                match = movies[movies["title"] == ft]
                if not match.empty:
                    trending_movies.append(ft)
                    existing_titles.add(ft)
            if len(trending_movies) >= 8:
                break

        # Still not enough? Grab top-rated movies from dataset
        if len(trending_movies) < 8:
            remaining_needed = 8 - len(trending_movies)
            for _, row in movies.head(50).iterrows():
                t = str(row.get("title", ""))
                if t and t not in existing_titles:
                    trending_movies.append(t)
                    existing_titles.add(t)
                if len(trending_movies) >= 8:
                    break

    trending_movies = trending_movies[:8]

    if not trending_movies:
        render_empty_state("🎬", "Loading Trending Movies...", "Click 'Get Recommendations' to explore.")
        return

    # Render trending cards
    cols = st.columns(len(trending_movies), gap="small")
    for i, title in enumerate(trending_movies):
        with cols[i]:
            _render_trending_card(title, i)

    # View All button
    _, _, _, _, va_col = st.columns([1, 1, 1, 1, 1])
    with va_col:
        if st.button("View All →", key="trending_view_all", use_container_width=True):
            st.session_state["page"] = "Movies"
            st.rerun()

    spacer("large")


def _render_trending_card(title: str, index: int):
    """Render a single compact trending movie card using st.html() to avoid sanitization."""
    year = _extract_year(title)
    short_title = _strip_year(title)

    poster_url = None
    tmdb_rating = None
    try:
        tmdb = get_enriched_movie(title) or {}
        poster_url = tmdb.get("poster_url")
        tmdb_rating = tmdb.get("tmdb_rating")
    except Exception:
        pass

    try:
        rating_num = float(tmdb_rating) if tmdb_rating is not None else 8.0
    except (ValueError, TypeError):
        rating_num = 8.0

    if poster_url and isinstance(poster_url, str) and poster_url.startswith("http"):
        poster_inner = f'<img src="{poster_url}" alt="{short_title}" style="width:100%;height:100%;object-fit:cover;display:block;">'
    else:
        poster_inner = f'<div style="width:100%;height:100%;background:#1a1a1a;display:flex;align-items:center;justify-content:center;color:#666;font-size:0.8rem;text-align:center;padding:0.5rem;">{short_title}</div>'

    # Use st.html() to bypass Streamlit's HTML sanitizer
    st.html(f"""
    <style>
        .tc {{
            background: #141414;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        .tc:hover {{
            transform: translateY(-6px);
            border-color: rgba(229,9,20,0.4);
            box-shadow: 0 12px 35px rgba(0,0,0,0.7), 0 0 15px rgba(229,9,20,0.12);
        }}
        .tc-poster {{
            position: relative;
            width: 100%;
            aspect-ratio: 2/3;
            overflow: hidden;
            background: #1a1a1a;
        }}
        .tc-poster img {{
            transition: transform 0.4s ease;
        }}
        .tc:hover .tc-poster img {{
            transform: scale(1.06);
        }}
        .tc-info {{
            padding: 0.6rem 0.7rem;
        }}
        .tc-title {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #FFFFFF;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 0.25rem;
        }}
        .tc-meta {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.72rem;
            color: #8A8A8A;
        }}
        .tc-star {{
            color: #FFD700;
            font-weight: 700;
        }}
    </style>
    <div class="tc">
        <div class="tc-poster">{poster_inner}</div>
        <div class="tc-info">
            <div class="tc-title">{short_title}</div>
            <div class="tc-meta">
                <span class="tc-star">★ {rating_num:.1f}</span>
                <span>{year if year else "Classic"}</span>
            </div>
        </div>
    </div>
    """)

    # Action button (Details)
    if st.button("Details", key=f"trend_details_{index}", use_container_width=True):
        st.session_state["selected_movie"] = title
        st.session_state["page"] = "Movie Details"
        st.rerun()


# ─── GENRES SECTION ───────────────────────────────────────────────────────────

def _render_genres_section(movies):
    """Render attractive circular icon genre cards."""

    # Section header with View All
    st.markdown("""
    <div class="section-header-row">
        <div class="section-header-left">
            <div style="font-size:1.4rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px;">Explore Genres</div>
            <div style="font-size:0.85rem;color:#8A8A8A;margin-top:0.2rem;">Dive into your favorite movie genres</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    genres = [
        ("Action", "💥"),
        ("Adventure", "🧭"),
        ("Animation", "✨"),
        ("Comedy", "🎭"),
        ("Crime", "🕵️"),
        ("Drama", "🎬"),
        ("Fantasy", "🔮"),
        ("Horror", "👻"),
        ("Romance", "❤️"),
        ("Sci-Fi", "🚀"),
        ("Thriller", "⚡"),
    ]

    # Render in a single row (11 cols) on desktop, wraps on mobile
    gcols = st.columns(len(genres), gap="small")
    for i, (gname, icon) in enumerate(genres):
        with gcols[i]:
            st.markdown(f"""
            <div class="genre-visual-card">
                <div class="genre-icon-circle">{icon}</div>
                <div class="genre-visual-title">{gname}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{gname}", key=f"btn_genre_{gname}", use_container_width=True):
                st.session_state["selected_genre"] = gname
                st.session_state["page"] = "Movies"
                st.rerun()

    # View All button
    _, _, _, _, va_col2 = st.columns([1, 1, 1, 1, 1])
    with va_col2:
        if st.button("View All →", key="genres_view_all", use_container_width=True):
            st.session_state["page"] = "Movies"
            st.rerun()

    spacer("large")
