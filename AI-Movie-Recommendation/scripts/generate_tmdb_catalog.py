"""Generate a refreshed Hindi/English movie catalog from TMDB Discover.

Run from the project root:
    python scripts/generate_tmdb_catalog.py
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SECRETS_PATH = PROJECT_ROOT / ".streamlit" / "secrets.toml"
OUTPUT_PATH = PROJECT_ROOT / "data" / "tmdb_movies.csv"
TMDB_BASE = "https://api.themoviedb.org/3"
REQUEST_TIMEOUT = 20

FIELDS = [
    "tmdb_id",
    "title",
    "original_title",
    "overview",
    "genres",
    "release_date",
    "original_language",
    "poster_path",
    "backdrop_path",
    "vote_average",
    "vote_count",
    "popularity",
]


def _read_api_key() -> str:
    """Read the existing TMDB key without adding a dependency."""
    if not SECRETS_PATH.exists():
        raise SystemExit(f"Missing TMDB secrets file: {SECRETS_PATH}")
    for line in SECRETS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("api_key") and "=" in line:
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
    raise SystemExit("TMDB api_key was not found in .streamlit/secrets.toml")


def _get_json(session: requests.Session, path: str, params: dict[str, Any]) -> dict[str, Any]:
    response = session.get(
        f"{TMDB_BASE}/{path}",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _discover_language(
    session: requests.Session,
    api_key: str,
    language: str,
    target_count: int,
    region: str | None = None,
) -> list[dict[str, Any]]:
    """Collect popular, sufficiently voted movies for one original language."""
    results: dict[int, dict[str, Any]] = {}
    page = 1
    max_pages = 40
    while len(results) < target_count and page <= max_pages:
        params: dict[str, Any] = {
            "api_key": api_key,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "page": page,
            "with_original_language": language,
            "primary_release_date.gte": "2006-01-01",
            "primary_release_date.lte": "2026-12-31",
            "vote_count.gte": 20 if language == "hi" else 100,
        }
        if region:
            params["region"] = region

        payload = _get_json(session, "discover/movie", params)
        page_results = payload.get("results", [])
        if not page_results:
            break
        for movie in page_results:
            movie_id = movie.get("id")
            if movie_id and movie_id not in results:
                results[movie_id] = movie
        page += 1
        time.sleep(0.08)

        total_pages = min(int(payload.get("total_pages", page)), max_pages)
        if page > total_pages:
            break

    return list(results.values())[:target_count]


def _genre_map(session: requests.Session, api_key: str) -> dict[int, str]:
    payload = _get_json(
        session,
        "genre/movie/list",
        {"api_key": api_key, "language": "en-US"},
    )
    return {int(item["id"]): item["name"] for item in payload.get("genres", [])}


def _normalise(movie: dict[str, Any], genres: dict[int, str]) -> dict[str, Any]:
    release_date = str(movie.get("release_date") or "")
    return {
        "tmdb_id": int(movie["id"]),
        "title": str(movie.get("title") or "").strip(),
        "original_title": str(movie.get("original_title") or "").strip(),
        "overview": str(movie.get("overview") or "").strip(),
        "genres": "|".join(genres[g] for g in movie.get("genre_ids", []) if g in genres),
        "release_date": release_date,
        "original_language": str(movie.get("original_language") or "").strip(),
        "poster_path": movie.get("poster_path") or "",
        "backdrop_path": movie.get("backdrop_path") or "",
        "vote_average": float(movie.get("vote_average") or 0),
        "vote_count": int(movie.get("vote_count") or 0),
        "popularity": float(movie.get("popularity") or 0),
    }


def generate_catalog(hindi_count: int = 600, english_count: int = 300) -> Path:
    api_key = _read_api_key()
    session = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"Accept": "application/json", "User-Agent": "CineAI/1.0"})

    genre_names = _genre_map(session, api_key)
    hindi = _discover_language(session, api_key, "hi", hindi_count, region="IN")
    english = _discover_language(session, api_key, "en", english_count)

    unique: dict[int, dict[str, Any]] = {}
    titles: set[str] = set()
    for movie in hindi + english:
        row = _normalise(movie, genre_names)
        title_key = row["title"].casefold()
        if row["title"] and row["release_date"] and title_key not in titles:
            unique[row["tmdb_id"]] = row
            titles.add(title_key)

    rows = list(unique.values())
    rows.sort(key=lambda row: (-row["popularity"], row["title"].lower()))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} movies to {OUTPUT_PATH}")
    print(f"Hindi: {sum(row['original_language'] == 'hi' for row in rows)}")
    print(f"English: {sum(row['original_language'] == 'en' for row in rows)}")
    return OUTPUT_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hindi", type=int, default=600)
    parser.add_argument("--english", type=int, default=300)
    args = parser.parse_args()
    generate_catalog(args.hindi, args.english)
