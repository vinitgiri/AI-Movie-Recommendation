"""Session-backed CineAI profile and preference state."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "Horror", "Mystery", "Romance",
    "Science Fiction", "Thriller", "War", "Western", "Children's",
    "Film-Noir", "Musical",
]
LANGUAGES = [
    "Hindi", "English", "Tamil", "Telugu", "Malayalam", "Kannada",
    "Bengali", "Marathi", "Punjabi", "Other",
]
ERAS = ["Any", "2020s", "2010s", "2000s", "1990s", "Classic"]

DEFAULT_PROFILE: dict[str, Any] = {
    "name": "Vinit",
    "username": "vinit",
    "bio": "Movie enthusiast discovering thoughtful recommendations.",
    "avatar_bytes": None,
    "favorite_genres": ["Drama", "Science Fiction"],
    "preferred_languages": ["English", "Hindi"],
    "preferred_era": "Any",
    "member_since": "2026",
    "updated_at": None,
}

DEFAULT_PREFERENCES: dict[str, Any] = {
    "alpha": 0.5,
    "recommendation_count": 10,
    "minimum_rating": 0.0,
    "minimum_vote_count": 0,
    "popularity_influence": 0.0,
    "similarity_threshold": 0.0,
    "diversity": "Medium",
    "mode": "Hybrid Fusion",
    "include_genres": [],
    "exclude_genres": [],
    "from_year": 2006,
    "to_year": 2026,
    "rating_min": 0.0,
    "rating_max": 10.0,
    "popularity": "Any",
    "runtime": "Any",
    "language_mode": "Preferred language",
    "use_rating_history": True,
    "use_favorites": True,
    "use_search_history": True,
    "use_recently_viewed": True,
    "use_liked_genres": True,
    "use_disliked_genres": True,
    "use_interaction_history": True,
    "theme": "Dark",
    "card_density": "Comfortable",
    "poster_size": "Medium",
    "grid_columns": "Auto",
    "show_ratings": True,
    "show_genres": True,
    "show_release_year": True,
    "show_overview": True,
    "show_popularity": False,
    "show_recommendation_score": True,
    "display_language": "English",
    "save_recommendation_history": True,
    "save_search_history": True,
    "save_viewed_movies": True,
    "save_rating_history": True,
    "allow_activity_personalization": True,
    "explain_recommendations": True,
}


def initialize_profile_state() -> None:
    """Initialize all profile data once per Streamlit session."""
    if "profile" not in st.session_state:
        st.session_state["profile"] = DEFAULT_PROFILE.copy()
    if "profile_preferences" not in st.session_state:
        st.session_state["profile_preferences"] = DEFAULT_PREFERENCES.copy()
    if "recommendation_history" not in st.session_state:
        st.session_state["recommendation_history"] = []
    if "search_history" not in st.session_state:
        st.session_state["search_history"] = []
    if "profile_update_at" not in st.session_state:
        st.session_state["profile_update_at"] = None
    if "profile_menu_section" not in st.session_state:
        st.session_state["profile_menu_section"] = None


def profile() -> dict[str, Any]:
    initialize_profile_state()
    return st.session_state["profile"]


def preferences() -> dict[str, Any]:
    initialize_profile_state()
    return st.session_state["profile_preferences"]


def save_profile(values: dict[str, Any]) -> None:
    initialize_profile_state()
    st.session_state["profile"].update(values)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state["profile"]["updated_at"] = now
    st.session_state["profile_update_at"] = now


def update_preferences(values: dict[str, Any]) -> None:
    initialize_profile_state()
    st.session_state["profile_preferences"].update(values)
    st.session_state["alpha_weight"] = max(0.0, min(1.0, float(values.get("alpha", preferences()["alpha"]))))


def reset_personalization() -> None:
    prefs = preferences()
    for key in (
        "use_rating_history", "use_favorites", "use_search_history",
        "use_recently_viewed", "use_liked_genres", "use_disliked_genres",
        "use_interaction_history", "include_genres", "exclude_genres",
    ):
        prefs[key] = DEFAULT_PREFERENCES[key]


def reset_preferences() -> None:
    """Restore recommendation and display preferences for this session."""
    st.session_state["profile_preferences"] = DEFAULT_PREFERENCES.copy()
    st.session_state["alpha_weight"] = DEFAULT_PREFERENCES["alpha"]


def profile_completion() -> int:
    p = profile()
    checks = [p.get("name"), p.get("username"), p.get("bio"), p.get("favorite_genres"), p.get("preferred_languages"), p.get("preferred_era")]
    return int(round(sum(bool(item) for item in checks) / len(checks) * 100))
