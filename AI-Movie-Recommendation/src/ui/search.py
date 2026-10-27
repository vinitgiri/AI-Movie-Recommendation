"""
src/ui/search.py
----------------
CineAI Full-Page Search — Interactive real-time search across 3,883 MovieLens titles
with genre filtering and TMDB poster cards.
"""

from __future__ import annotations

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
    """Render the full-page search experience."""
    inject_global_css()
    render_navbar("Search")

    movies, ratings, users, hybrid_model, collab_model, missing = load_models()
    if missing:
        models_missing_error(missing)
        st.stop()

    catalog = load_tmdb_catalog()
    if not catalog.empty:
        movies = catalog

    render_section_header(
        "SEARCH",
        "Search Film Database",
        "Find any film by title, keyword, or genre from the MovieLens 1M repository.",
    )

    # Search Bar & Genre Filter
    s_col, g_col = st.columns([3, 1], gap="medium")

    with s_col:
        query = st.text_input(
            "Search Movie Titles",
            placeholder="e.g. Matrix, Godfather, Star Wars, Toy Story...",
            key="search_query_input",
            label_visibility="collapsed",
        ).strip()

    with g_col:
        genre_filter = st.selectbox(
            "Filter by Genre",
            ["All Genres", "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller"],
            index=0,
            label_visibility="collapsed",
        )

    # Search Execution
    results = movies.copy()

    if genre_filter != "All Genres":
        results = results[results["genres"].str.contains(genre_filter, case=False, na=False)]

    if query:
        results = results[results["title"].str.contains(query, case=False, na=False)]

    if query or genre_filter != "All Genres":
        total_found = len(results)
        st.markdown(f"""
        <div style="font-size:0.85rem;color:#888;margin:1rem 0 1.2rem;">
            Found <strong>{total_found:,}</strong> movies matching your query
        </div>
        """, unsafe_allow_html=True)

        if total_found > 0:
            render_movie_grid(
                results.head(25),
                cols=5,
                key_prefix="search_results",
                show_rank=False,
                score_col=None,
                show_actions=True,
                fetch_tmdb=True,
            )
        else:
            render_empty_state(
                "🔍",
                f"No results found for '{query}'",
                "Try checking spelling or using a more general keyword.",
            )
    else:
        # Default popular suggestions
        st.markdown("""
        <div style="font-size:0.85rem;font-weight:700;letter-spacing:1.5px;color:#E50914;margin:1.5rem 0 0.8rem;text-transform:uppercase;">
            POPULAR SEARCH SUGGESTIONS
        </div>
        """, unsafe_allow_html=True)

        popular_df = movies.head(5)
        render_movie_grid(
            popular_df,
            cols=5,
            key_prefix="search_popular",
            show_rank=False,
            score_col=None,
            show_actions=True,
            fetch_tmdb=True,
        )

    spacer("large")
    render_footer()
