"""
src/components/movie_card.py
----------------------------
Reusable movie card components with posters, badges, metadata,
score breakdown bars, and interactive actions.
"""

from __future__ import annotations

import re
from typing import Optional

import streamlit as st

from src.tmdb import get_enriched_movie


def strip_year(title: str) -> str:
    """Remove year suffix like '(1995)' from movie title."""
    return re.sub(r"\s*\(\d{4}\)\s*$", "", str(title)).strip()


def extract_year(title: str) -> str:
    """Extract 4-digit year from movie title."""
    m = re.search(r"\((\d{4})\)$", str(title).strip())
    return m.group(1) if m else ""


def format_genres_html(genres_str: str, max_genres: int = 2) -> str:
    """Return compact HTML genre tags."""
    if not genres_str:
        return ""
    genres = str(genres_str).replace("|", " ").split()[:max_genres]
    return "".join(f'<span class="genre-tag">{g}</span>' for g in genres)


def movie_card_html(
    title: str,
    genres: str = "",
    hybrid_score: Optional[float] = None,
    rank: Optional[int] = None,
    tmdb_rating: Optional[float] = None,
    poster_path: Optional[str] = None,
    year: str = "",
) -> str:
    """
    Generate clean, self-contained HTML for a single movie card.
    """
    clean_name = strip_year(title)
    if not year:
        year = extract_year(title)

    # Poster or stylish fallback
    if poster_path:
        poster_html = f'<img class="movie-poster-img" src="{poster_path}" alt="{clean_name}" loading="lazy">'
    else:
        genre_hint = genres.replace("|", " • ")[:25] if genres else ""
        poster_html = f"""
        <div class="movie-poster-fallback">
            <div class="fallback-icon">🎬</div>
            <div class="fallback-title">{clean_name}</div>
            <div style="font-size:0.65rem;color:#666;margin-top:0.3rem;">{genre_hint}</div>
        </div>
        """

    # AI Match badge
    ai_badge_html = ""
    if hybrid_score is not None and hybrid_score > 0:
        pct = int(min(round(hybrid_score * 100), 100))
        ai_badge_html = f'<div class="badge-ai-match">⚡ {pct}% MATCH</div>'

    # Rank badge
    rank_badge_html = ""
    if rank is not None:
        rank_badge_html = f'<div class="badge-rank">#{rank}</div>'

    # Sub-meta: Year + Rating
    meta_sub_parts = []
    if year:
        meta_sub_parts.append(f"<span>{year}</span>")
    if tmdb_rating and tmdb_rating > 0:
        meta_sub_parts.append(f'<span class="rating-star">★ {tmdb_rating:.1f}</span>')
    sub_meta_html = " • ".join(meta_sub_parts)

    genre_tags_html = format_genres_html(genres, max_genres=2)

    return f"""
    <div class="movie-card">
        <div class="movie-poster-wrap">
            {rank_badge_html}
            {ai_badge_html}
            {poster_html}
        </div>
        <div class="movie-meta-wrap">
            <div class="movie-card-name" title="{clean_name}">{clean_name}</div>
            <div class="movie-card-sub">
                {sub_meta_html if sub_meta_html else '&nbsp;'}
            </div>
            <div>
                {genre_tags_html if genre_tags_html else '&nbsp;'}
            </div>
        </div>
    </div>
    """


def render_score_breakdown(
    content_score: Optional[float] = None,
    collaborative_score: Optional[float] = None,
    hybrid_score: Optional[float] = None,
    fallback_used: bool = False,
):
    """Render visual score breakdown bars showing WHY the movie was recommended."""
    st.markdown('<div class="ai-control-header" style="margin-top:0.5rem;">AI SCORE EXPLANATION</div>', unsafe_allow_html=True)

    if content_score is not None:
        c_pct = int(min(round(content_score * 100), 100))
        st.markdown(f"""
        <div class="score-metric-row">
            <div class="score-metric-header">
                <span class="score-metric-label">Content Similarity (Genre Vector)</span>
                <span class="score-metric-val">{c_pct}%</span>
            </div>
            <div class="score-metric-track">
                <div class="score-metric-fill" style="width:{c_pct}%;background:linear-gradient(90deg,#E50914,#FF6B6B);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not fallback_used and collaborative_score is not None:
        cf_pct = int(min(round((collaborative_score / 5.0) * 100), 100))
        st.markdown(f"""
        <div class="score-metric-row">
            <div class="score-metric-header">
                <span class="score-metric-label">Collaborative SVD (Predicted {collaborative_score:.2f}★)</span>
                <span class="score-metric-val">{cf_pct}%</span>
            </div>
            <div class="score-metric-track">
                <div class="score-metric-fill" style="width:{cf_pct}%;background:linear-gradient(90deg,#58A6FF,#79C0FF);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if hybrid_score is not None:
        h_pct = int(min(round(hybrid_score * 100), 100))
        st.markdown(f"""
        <div class="score-metric-row">
            <div class="score-metric-header">
                <span class="score-metric-label">Final Weighted Hybrid Fusion</span>
                <span class="score-metric-val">{h_pct}%</span>
            </div>
            <div class="score-metric-track">
                <div class="score-metric-fill" style="width:{h_pct}%;background:linear-gradient(90deg,#3FB950,#56D364);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if fallback_used:
        st.caption("ℹ️ Cold-start user: pure content-based similarity was applied.")


def render_movie_card_with_actions(
    row_or_title,
    idx_key: str,
    rank: Optional[int] = None,
    hybrid_score: Optional[float] = None,
    content_score: Optional[float] = None,
    collaborative_score: Optional[float] = None,
    fallback_used: bool = False,
    show_similar_btn: bool = True,
):
    """
    Renders a complete movie card with working Streamlit actions:
    - View Details
    - Toggle Favorite
    - Find Similar Movies
    """
    if isinstance(row_or_title, str):
        title = row_or_title
        genres = ""
    else:
        title = row_or_title.get("title", "")
        genres = row_or_title.get("genres", "")

    # Fetch TMDB enrichment
    poster_path = None
    tmdb_rating = None
    try:
        tmdb_info = get_enriched_movie(title)
        poster_path = tmdb_info.get("poster_url")
        tmdb_rating = tmdb_info.get("tmdb_rating")
    except Exception:
        pass

    # Render visual card
    st.markdown(
        movie_card_html(
            title=title,
            genres=genres,
            hybrid_score=hybrid_score,
            rank=rank,
            tmdb_rating=tmdb_rating,
            poster_path=poster_path,
        ),
        unsafe_allow_html=True,
    )

    # Actions: Details & Favorite
    btn_c1, btn_c2 = st.columns([1.2, 1], gap="small")
    with btn_c1:
        if st.button("Details", key=f"det_{idx_key}", use_container_width=True):
            st.session_state["selected_movie_detail"] = title
            if "recently_viewed" not in st.session_state:
                st.session_state["recently_viewed"] = []
            if title not in st.session_state["recently_viewed"]:
                st.session_state["recently_viewed"].insert(0, title)
                st.session_state["recently_viewed"] = st.session_state["recently_viewed"][:20]
            st.session_state["page"] = "Movie Details"
            st.rerun()

    with btn_c2:
        if "favorites" not in st.session_state:
            st.session_state["favorites"] = []
        is_fav = title in st.session_state["favorites"]
        fav_icon = "❤️" if is_fav else "🤍"
        if st.button(fav_icon, key=f"fav_{idx_key}", help="Toggle Favorite", use_container_width=True):
            if is_fav:
                st.session_state["favorites"].remove(title)
                st.toast(f"Removed '{strip_year(title)}' from favorites")
            else:
                st.session_state["favorites"].append(title)
                st.toast(f"Added '{strip_year(title)}' to favorites! ❤️")
            st.rerun()
