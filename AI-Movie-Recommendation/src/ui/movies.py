"""
src/ui/movies.py
----------------
CineAI Catalog Browser — Responsive movie grid with real-time genre filtering,
decade slicing, sorting options, and pagination.
"""

from __future__ import annotations

import re
import pandas as pd
import streamlit as st

from src.ui.styles import inject_global_css
from src.ui.navigation import render_navbar, render_footer
from src.ui.components import (
    render_section_header,
    render_movie_grid,
    render_empty_state,
    spacer,
)
from src.components.model_loader import load_models, models_missing_error
from src.tmdb_catalog import load_tmdb_catalog


def render():
    """Render the Explore Movies catalog browser."""
    inject_global_css()
    render_navbar("Movies")

    movies, ratings, users, hybrid_model, collab_model, missing = load_models()
    if missing:
        models_missing_error(missing)
        st.stop()

    catalog = load_tmdb_catalog()
    if not catalog.empty:
        movies = catalog

    render_section_header(
        "CATALOG",
        "Explore Movie Catalog",
            f"Browse {len(movies):,} Hindi and English films enriched with TMDB metadata.",
    )

    # Filter Bar
    f1, f2, f3, f4 = st.columns([1.5, 1.2, 1.3, 1], gap="small")

    # Genre list
    all_genres = ["All Genres"] + sorted([
        "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime",
        "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
        "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
    ])

    selected_genre_state = st.session_state.get("selected_genre", "All Genres")
    default_genre_idx = all_genres.index(selected_genre_state) if selected_genre_state in all_genres else 0

    with f1:
        genre_filter = st.selectbox("Genre Filter", all_genres, index=default_genre_idx)
        st.session_state["selected_genre"] = genre_filter

    with f2:
        decade_filter = st.selectbox(
            "Era / Decade",
                ["All Eras", "2020s", "2010s", "2000s", "1990s", "1980s", "1970s", "1960s", "1950s & Older"],
            index=0,
        )

    with f3:
        sort_by = st.selectbox(
            "Sort Order",
            ["Alphabetical (A – Z)", "Alphabetical (Z – A)", "Most Rated", "Highest Rated"],
            index=0,
        )

    with f4:
        page_size = st.selectbox("Items per Page", [15, 25, 50], index=0)

    # Filter pipeline
    df = movies.copy()

    # Genre filter
    if genre_filter != "All Genres":
        df = df[df["genres"].str.contains(genre_filter, case=False, na=False)]

    # Decade filter
    if decade_filter != "All Eras":
        def _matches_decade(title):
            m = re.search(r"\((\d{4})\)", str(title))
            if not m:
                return False
            yr = int(m.group(1))
            if decade_filter == "1990s":
                return 1990 <= yr <= 1999
            elif decade_filter == "1980s":
                return 1980 <= yr <= 1989
            elif decade_filter == "1970s":
                return 1970 <= yr <= 1979
            elif decade_filter == "1960s":
                return 1960 <= yr <= 1969
            elif decade_filter == "1950s & Older":
                return yr < 1960
            return True

        df = df[df["title"].apply(_matches_decade)]

    # Sorting
    if sort_by == "Alphabetical (A – Z)":
        df = df.sort_values("title", ascending=True)
    elif sort_by == "Alphabetical (Z – A)":
        df = df.sort_values("title", ascending=False)
    elif sort_by in ("Most Rated", "Highest Rated"):
        if "vote_count" in df.columns:
            df["count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
            df["mean"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
        else:
            r_counts = ratings.groupby("movieId")["rating"].agg(["count", "mean"]).reset_index()
            df = df.merge(r_counts, on="movieId", how="left")
        if sort_by == "Most Rated":
            df = df.sort_values("count", ascending=False)
        else:
            df = df[df["count"] >= 30].sort_values("mean", ascending=False)

    total_matches = len(df)

    # Pagination controls
    total_pages = max(1, (total_matches + page_size - 1) // page_size)
    if "movies_page_idx" not in st.session_state:
        st.session_state["movies_page_idx"] = 1

    current_p = min(st.session_state["movies_page_idx"], total_pages)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin:1.2rem 0 1rem;font-size:0.85rem;color:#888;">
        <span>Showing <strong>{min(total_matches, page_size)}</strong> of <strong>{total_matches:,}</strong> matching films</span>
        <span>Page <strong>{current_p}</strong> of <strong>{total_pages}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    start_idx = (current_p - 1) * page_size
    page_df = df.iloc[start_idx : start_idx + page_size]

    if not page_df.empty:
        render_movie_grid(
            page_df,
            cols=5,
            key_prefix="movies_browse",
            show_rank=False,
            score_col=None,
            show_actions=True,
            fetch_tmdb=True,
        )

        # Pagination Buttons
        pcol1, pcol2, pcol3, pcol4 = st.columns([1, 1, 1, 3], gap="small")
        with pcol1:
            if st.button("❮ Previous", disabled=(current_p <= 1), use_container_width=True):
                st.session_state["movies_page_idx"] = max(1, current_p - 1)
                st.rerun()
        with pcol2:
            if st.button("Next ❯", disabled=(current_p >= total_pages), use_container_width=True):
                st.session_state["movies_page_idx"] = min(total_pages, current_p + 1)
                st.rerun()
    else:
        render_empty_state("🔍", "No Movies Found", "Try broadening your genre or decade filter criteria.")

    spacer("large")
    render_footer()
