"""
src/tmdb.py
-----------
TMDB API integration for enriching movie UI with posters, backdrops,
overviews, runtime, and metadata.

CRITICAL: This module ONLY fetches visual/metadata enrichment.
It never supplies recommendations. All recommendations come from
the ML backend (TF-IDF, SVD, Hybrid).

Requires TMDB_API_KEY in .streamlit/secrets.toml:
    [tmdb]
    api_key = "your_key_here"

If the key is missing or TMDB is unavailable, all functions return
gracefully with None / empty values — the app continues without posters.
"""

from __future__ import annotations

import re
import time
from typing import Optional

import requests
import streamlit as st

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
REQUEST_TIMEOUT = 8  # seconds


def _get_api_key() -> Optional[str]:
    """Return TMDB API key from Streamlit secrets, or None if not configured."""
    try:
        return st.secrets["tmdb"]["api_key"]
    except (KeyError, FileNotFoundError):
        return None


def _clean_title(title: str) -> str:
    """Strip year suffix like '(1999)' from MovieLens titles."""
    return re.sub(r"\s*\(\d{4}\)\s*$", "", title).strip()


def _extract_year(title: str) -> Optional[int]:
    """Extract year from MovieLens title format 'Movie Title (YYYY)'."""
    match = re.search(r"\((\d{4})\)\s*$", title)
    return int(match.group(1)) if match else None


@st.cache_data(ttl=86400, show_spinner=False)
def search_movie(title: str) -> Optional[dict]:
    """
    Search TMDB for a movie by title. Returns the best matching result dict,
    or None if not found / API unavailable.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    clean = _clean_title(title)
    year = _extract_year(title)

    params = {"api_key": api_key, "query": clean, "include_adult": False}
    if year:
        params["year"] = year

    try:
        resp = requests.get(
            f"{TMDB_BASE}/search/movie",
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results:
            return results[0]
        # Try without year constraint if year-filtered search fails
        if year:
            params.pop("year", None)
            resp2 = requests.get(
                f"{TMDB_BASE}/search/movie",
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            resp2.raise_for_status()
            results2 = resp2.json().get("results", [])
            if results2:
                return results2[0]
    except Exception:  # noqa: BLE001
        pass
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_movie_details(tmdb_id: int) -> Optional[dict]:
    """Fetch full movie details from TMDB by movie ID."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        resp = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": api_key},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:  # noqa: BLE001
        return None


def poster_url(path: Optional[str], size: str = "w342") -> Optional[str]:
    """Build a TMDB poster URL from a poster_path. Returns None if path is absent."""
    if not path:
        return None
    return f"{TMDB_IMAGE_BASE}/{size}{path}"


def backdrop_url(path: Optional[str], size: str = "w1280") -> Optional[str]:
    """Build a TMDB backdrop URL from a backdrop_path."""
    if not path:
        return None
    return f"{TMDB_IMAGE_BASE}/{size}{path}"


@st.cache_data(ttl=86400, show_spinner=False)
def get_enriched_movie(title: str) -> dict:
    """
    Return a dict with TMDB enrichment for a movie.
    All fields fall back gracefully if TMDB is unavailable.

    Keys returned:
        poster_url, backdrop_url, overview, tmdb_rating,
        tmdb_votes, runtime, release_date, tmdb_genres, tmdb_id
    """
    result = {
        "poster_url": None,
        "backdrop_url": None,
        "overview": None,
        "tmdb_rating": None,
        "tmdb_votes": None,
        "runtime": None,
        "release_date": None,
        "tmdb_genres": [],
        "tmdb_id": None,
    }

    search = search_movie(title)
    if not search:
        return result

    tmdb_id = search.get("id")
    result["tmdb_id"] = tmdb_id
    result["poster_url"] = poster_url(search.get("poster_path"))
    result["backdrop_url"] = backdrop_url(search.get("backdrop_path"))
    result["overview"] = search.get("overview") or None
    result["tmdb_rating"] = search.get("vote_average")
    result["tmdb_votes"] = search.get("vote_count")
    result["release_date"] = search.get("release_date")

    # Fetch details for runtime and genres
    if tmdb_id:
        details = get_movie_details(tmdb_id)
        if details:
            result["runtime"] = details.get("runtime")
            result["tmdb_genres"] = [g["name"] for g in details.get("genres", [])]
            if not result["overview"]:
                result["overview"] = details.get("overview")

    return result


def format_runtime(minutes: Optional[int]) -> str:
    """Format runtime in minutes to '2h 22m' style."""
    if not minutes:
        return ""
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"
