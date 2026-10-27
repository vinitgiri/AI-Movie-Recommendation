"""
src/ui/favorites.py
-------------------
CineAI Favorites & Watchlist — Persistent session-state favorites manager
with one-click removal, empty state illustrations, and recently viewed history.
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


def render():
    """Render the Favorites & Watchlist management page."""
    inject_global_css()
    render_navbar("Favorites")

    movies, ratings, users, hybrid_model, collab_model, missing = load_models()
    if missing:
        models_missing_error(missing)
        st.stop()

    fav_list = st.session_state.get("favorites", [])

    h_col, act_col = st.columns([4, 1])
    with h_col:
        render_section_header(
            "WATCHLIST",
            "My Saved Favorites",
            "Your curated personal collection of saved films and bookmarks.",
        )
    with act_col:
        if fav_list:
            st.markdown("<div style='height:2.8rem;'></div>", unsafe_allow_html=True)
            if st.button("Clear Watchlist", key="btn_clear_favs", use_container_width=True):
                st.session_state["favorites"] = []
                st.toast("Watchlist cleared.")
                st.rerun()

    if fav_list:
        fav_df = movies[movies["title"].isin(fav_list)]
        render_movie_grid(
            fav_df,
            cols=5,
            key_prefix="fav_grid",
            show_rank=False,
            score_col=None,
            show_actions=True,
            fetch_tmdb=True,
        )
    else:
        render_empty_state(
            "🤍",
            "Your Watchlist is Empty",
            "Click the heart (🤍) icon on any movie card or detail page to save it here for quick access.",
        )
        c1, c2, c3 = st.columns([1.5, 1, 1.5])
        with c2:
            if st.button("Explore Movies Now", key="fav_empty_explore", type="primary", use_container_width=True):
                st.session_state["page"] = "Movies"
                st.rerun()

    # Recently Viewed History Section
    recently_viewed = st.session_state.get("recently_viewed", [])
    if recently_viewed:
        spacer("medium")
        render_section_header(
            "HISTORY",
            "Recently Viewed",
            "Titles you inspected during this session.",
        )
        recent_df = movies[movies["title"].isin(recently_viewed[:10])]
        render_movie_grid(
            recent_df,
            cols=5,
            key_prefix="recent_grid",
            show_rank=False,
            score_col=None,
            show_actions=True,
            fetch_tmdb=True,
        )

    spacer("large")
    render_footer()
