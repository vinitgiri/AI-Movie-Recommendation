"""
app.py
------
CineAI — AI-Based Personalized Movie Recommendation System.
Main entrypoint and clean routing to modular src.ui components.
"""

from __future__ import annotations

import streamlit as st

from src.profile import initialize_profile_state

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CINEAI — AI Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State Initialization ──────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

if "recently_viewed" not in st.session_state:
    st.session_state["recently_viewed"] = []

if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = None

if "selected_genre" not in st.session_state:
    st.session_state["selected_genre"] = "All Genres"

if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = 1

if "alpha_weight" not in st.session_state:
    st.session_state["alpha_weight"] = 0.5

initialize_profile_state()

# ── Modular UI Routing ────────────────────────────────────────────────────────
from src.ui import (
    home,
    recommendations,
    movies,
    search,
    favorites,
    analytics,
    about,
    movie_details,
)

PAGE_ROUTER = {
    "Home": home.render,
    "Recommendations": recommendations.render,
    "Movies": movies.render,
    "Search": search.render,
    "Favorites": favorites.render,
    "Analytics": analytics.render,
    "About": about.render,
    "Movie Details": movie_details.render,
}

current_page = st.session_state.get("page", "Home")
render_func = PAGE_ROUTER.get(current_page, home.render)
render_func()
