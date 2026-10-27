"""
src/ui/components.py
--------------------
Reusable visual components for CineAI:
  - Section headers
  - Movie cards & responsive grids with TMDB poster fallbacks
  - Score breakdown bars
  - Stat cards & empty states
"""

from __future__ import annotations

import hashlib
import re
from typing import Optional

import streamlit as st

from src.tmdb import get_enriched_movie


def _strip_year(title: Optional[str]) -> str:
    """Remove trailing (YYYY) from MovieLens titles."""
    if not title or not isinstance(title, str):
        return "Unknown Movie"
    return re.sub(r"\s*\(\d{4}\)\s*$", "", title).strip()


def _extract_year(title: Optional[str]) -> str:
    """Extract year from MovieLens title format."""
    if not title or not isinstance(title, str):
        return ""
    m = re.search(r"\((\d{4})\)\s*$", title.strip())
    return m.group(1) if m else ""


def _unique_key(prefix: str, title: Optional[str], index: int) -> str:
    """Generate a unique key for Streamlit widgets."""
    safe_title = str(title or "untitled")
    h = hashlib.md5(safe_title.encode("utf-8", errors="ignore")).hexdigest()[:6]
    return f"{prefix}_{index}_{h}"


def _genre_list(genres_str: Optional[str], max_n: int = 3) -> list[str]:
    """Parse pipe-separated genres into a list."""
    if not genres_str or not isinstance(genres_str, str):
        return []
    return genres_str.replace("|", " ").split()[:max_n]


def render_section_header(label: str, title: str, subtitle: str = ""):
    """Render a section header with label, headline, and subheadline."""
    sub_html = f'<div class="section-subheadline">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-top: 2.5rem; margin-bottom: 0.8rem;">
        <div class="section-eyebrow">{label}</div>
        <div class="section-headline">{title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(value: str, label: str):
    """Render a single high-impact stat card."""
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{value}</span>
        <span class="stat-card-tag">{label}</span>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, subtitle: str = ""):
    """Render an attractive dark empty state."""
    sub_html = f'<div style="font-size:0.85rem;color:#888888;max-width:460px;margin:0 auto;line-height:1.5;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="text-align:center;padding:3.5rem 1rem 3rem;">
        <div style="font-size:3rem;margin-bottom:0.8rem;color:#E50914;opacity:0.6;">{icon}</div>
        <div style="font-size:1.2rem;font-weight:700;color:#FFFFFF;margin-bottom:0.4rem;">{title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def _movie_card_html(
    title: str,
    poster_url: Optional[str] = None,
    year: str = "",
    genres: str = "",
    tmdb_rating: Optional[float] = None,
    hybrid_score: Optional[float] = None,
    rank: Optional[int] = None,
) -> str:
    """Build pure HTML markup for a movie card."""
    short = _strip_year(title)
    if not year:
        year = _extract_year(title)

    # Poster artwork or Pro SVG Fallback
    if poster_url and isinstance(poster_url, str) and poster_url.startswith("http"):
        poster_html = f'<img class="movie-poster-img" src="{poster_url}" alt="{short}" loading="lazy">'
    else:
        poster_html = f"""
        <div class="movie-poster-pro-fallback">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#E50914" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="14.31" y1="8" x2="20.05" y2="17.94"></line>
                <line x1="9.69" y1="8" x2="21.17" y2="8"></line>
                <line x1="7.38" y1="12" x2="13.12" y2="2.06"></line>
                <line x1="9.69" y1="16" x2="3.95" y2="6.06"></line>
                <line x1="14.31" y1="16" x2="2.83" y2="16"></line>
                <line x1="16.62" y1="12" x2="10.88" y2="21.94"></line>
            </svg>
            <div class="fb-title">{short}</div>
        </div>
        """

    # AI Match badge
    ai_badge = ""
    if hybrid_score is not None and isinstance(hybrid_score, (int, float)) and hybrid_score > 0:
        pct = int(min(round(float(hybrid_score) * 100), 100))
        ai_badge = f'<div class="badge-ai-pill">AI {pct}%</div>'

    # Rank badge
    rank_badge = f'<div class="badge-rank-pill">#{rank}</div>' if rank is not None else ""

    # Rating badge
    if tmdb_rating is not None and isinstance(tmdb_rating, (int, float)):
        rating_str = f"★ {float(tmdb_rating):.1f}"
    else:
        rating_str = "★ 4.0"

    # Genre pills
    genre_pills = "".join(
        f'<span class="genre-tag-pill">{g}</span>'
        for g in _genre_list(genres, max_n=2)
    )

    return f"""
    <div class="movie-card-box">
        <div class="movie-poster-frame">
            {rank_badge}
            {ai_badge}
            {poster_html}
        </div>
        <div class="movie-card-info-wrap">
            <div class="movie-card-main-title" title="{title}">{short}</div>
            <div class="movie-card-sub-meta">
                <span>{year if year else "Classic"}</span>
                <span style="color:#FFD700;font-weight:700;">{rating_str}</span>
            </div>
            <div style="margin-top:0.2rem;">
                {genre_pills}
            </div>
        </div>
    </div>
    """


def render_movie_card(
    title: str,
    genres: str = "",
    index: int = 0,
    key_prefix: str = "mc",
    hybrid_score: Optional[float] = None,
    rank: Optional[int] = None,
    show_actions: bool = True,
    fetch_tmdb: bool = True,
) -> Optional[str]:
    """
    Render a single movie card with poster and 3 action buttons.
    Returns the action taken ("details", "favorite", "similar", or None).
    """
    year = _extract_year(title)
    poster_url = None
    tmdb_rating = None

    if fetch_tmdb:
        try:
            tmdb = get_enriched_movie(title) or {}
            poster_url = tmdb.get("poster_url")
            tmdb_rating = tmdb.get("tmdb_rating")
        except Exception:
            pass

    card_html = _movie_card_html(
        title=title,
        poster_url=poster_url,
        year=year,
        genres=genres,
        tmdb_rating=tmdb_rating,
        hybrid_score=hybrid_score,
        rank=rank,
    )
    st.html(card_html)

    if not show_actions:
        return None

    # Three comfortable native action buttons
    c1, c2, c3 = st.columns([1.1, 0.9, 1.1], gap="small")
    action = None

    with c1:
        if st.button("Details", key=_unique_key(f"{key_prefix}_det", title, index), use_container_width=True):
            action = "details"

    with c2:
        is_fav = title in st.session_state.get("favorites", [])
        fav_icon = "❤️" if is_fav else "🤍"
        if st.button(fav_icon, key=_unique_key(f"{key_prefix}_fav", title, index), use_container_width=True):
            action = "favorite"

    with c3:
        if st.button("Similar", key=_unique_key(f"{key_prefix}_sim", title, index), use_container_width=True):
            action = "similar"

    return action


def render_movie_grid(
    movies_df,
    cols: int = 5,
    key_prefix: str = "grid",
    show_rank: bool = False,
    score_col: Optional[str] = "hybrid_score",
    show_actions: bool = True,
    fetch_tmdb: bool = True,
):
    """
    Render a responsive grid of movie cards and route clicked actions.
    """
    if movies_df is None or movies_df.empty:
        return

    columns = st.columns(cols, gap="small")

    for i, (_, row) in enumerate(movies_df.iterrows()):
        col = columns[i % cols]
        with col:
            title = str(row.get("title", "Unknown"))
            genres = str(row.get("genres", ""))
            hybrid_score = row.get(score_col) if score_col and score_col in row.index else None
            rank = (i + 1) if show_rank else None

            action = render_movie_card(
                title=title,
                genres=genres,
                index=i,
                key_prefix=key_prefix,
                hybrid_score=hybrid_score if (hybrid_score is not None and hybrid_score > 0) else None,
                rank=rank,
                show_actions=show_actions,
                fetch_tmdb=fetch_tmdb,
            )

            if action == "details":
                st.session_state["selected_movie"] = title
                _track_recently_viewed(title)
                st.session_state["page"] = "Movie Details"
                st.rerun()
            elif action == "favorite":
                _toggle_favorite(title)
                st.rerun()
            elif action == "similar":
                st.session_state["selected_movie"] = title
                st.session_state["page"] = "Movie Details"
                st.rerun()


def _track_recently_viewed(title: str):
    """Add a movie title to recently viewed history."""
    rv = st.session_state.get("recently_viewed", [])
    if title in rv:
        rv.remove(title)
    rv.insert(0, title)
    st.session_state["recently_viewed"] = rv[:20]


def _toggle_favorite(title: str):
    """Add or remove a movie from favorites in session state."""
    favs = st.session_state.get("favorites", [])
    if title in favs:
        favs.remove(title)
        st.toast(f"Removed '{_strip_year(title)}' from Favorites.")
    else:
        favs.append(title)
        st.toast(f"Added '{_strip_year(title)}' to Favorites!", icon="❤️")
    st.session_state["favorites"] = favs


def render_score_bars(
    content_score: Optional[float] = None,
    collaborative_score: Optional[float] = None,
    hybrid_score: Optional[float] = None,
    fallback_used: bool = False,
):
    """Render visual AI score breakdown progress bars."""
    st.markdown("""
    <div style="font-size:0.75rem;font-weight:800;letter-spacing:1.5px;color:#E50914;margin-bottom:0.8rem;text-transform:uppercase;">
        AI Score Composition
    </div>
    """, unsafe_allow_html=True)

    def _bar(label: str, value: float, color: str):
        pct = int(min(round(float(value) * 100), 100))
        st.markdown(f"""
        <div class="score-metric-row">
            <div class="score-metric-header">
                <span class="score-metric-label">{label}</span>
                <span class="score-metric-val">{pct}%</span>
            </div>
            <div class="score-metric-track">
                <div class="score-metric-fill" style="width:{pct}%;background:linear-gradient(90deg, {color}, {color}99);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if content_score is not None and content_score > 0:
        _bar("Content Similarity (TF-IDF)", content_score, "#E50914")

    if not fallback_used and collaborative_score is not None and collaborative_score > 0:
        norm_collab = min(float(collaborative_score) / 5.0, 1.0)
        _bar("Collaborative Score (SVD)", norm_collab, "#58A6FF")

    if hybrid_score is not None and hybrid_score > 0:
        _bar("Hybrid Ranking (α·Content + β·Collab)", float(hybrid_score), "#3FB950")

    if fallback_used:
        st.markdown("""
        <div class="cold-start-box" style="margin-top:0.8rem;">
            ℹ️ <strong>Cold-Start Mode:</strong> This user has limited rating history. Content-based similarity is prioritized.
        </div>
        """, unsafe_allow_html=True)


def spacer(size: str = "medium"):
    """Insert vertical spacing."""
    heights = {"small": "1rem", "medium": "2rem", "large": "3.5rem"}
    h = heights.get(size, "2rem")
    st.markdown(f'<div style="height:{h}"></div>', unsafe_allow_html=True)
