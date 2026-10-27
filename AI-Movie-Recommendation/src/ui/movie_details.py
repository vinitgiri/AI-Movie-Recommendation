"""
src/ui/movie_details.py
-----------------------
CineAI Cinematic Movie Details — High-res TMDB backdrop hero, detailed metadata,
AI similarity insights, and "More Like This" recommendations row.
"""

from __future__ import annotations

import streamlit as st

from src.ui.styles import inject_global_css
from src.ui.navigation import render_navbar, render_footer
from src.ui.components import (
    render_section_header,
    render_movie_grid,
    render_score_bars,
    _extract_year,
    _strip_year,
    spacer,
)
from src.components.model_loader import load_models, models_missing_error
from src.tmdb import get_enriched_movie


def render():
    """Render the cinematic movie detail view."""
    inject_global_css()
    render_navbar("Movie Details")

    movies, ratings, users, hybrid_model, collab_model, missing = load_models()
    if missing:
        models_missing_error(missing)
        st.stop()

    title = st.session_state.get("selected_movie")
    if not title:
        title = "Shawshank Redemption, The (1994)"
        st.session_state["selected_movie"] = title

    movie_row = movies[movies["title"] == title]
    if movie_row.empty:
        st.error(f"Movie '{title}' not found in catalog.")
        st.stop()

    movie_data = movie_row.iloc[0]
    short_title = _strip_year(title)
    year = _extract_year(title)
    genres_str = movie_data.get("genres", "").replace("|", " · ")

    # TMDB enrichment
    tmdb = {}
    try:
        tmdb = get_enriched_movie(title)
    except Exception:
        pass

    backdrop_url = tmdb.get("backdrop_url")
    poster_url = tmdb.get("poster_url")
    raw_overview = tmdb.get("overview")
    overview = raw_overview if (raw_overview and isinstance(raw_overview, str)) else "A landmark cinematic masterpiece in the MovieLens archive."
    tmdb_rating = tmdb.get("tmdb_rating") or 8.5
    runtime = tmdb.get("runtime")

    bg_style = f"background-image: url('{backdrop_url}');" if backdrop_url else "background: linear-gradient(135deg, #181818 0%, #0e0e0e 100%);"

    # ── Cinematic Backdrop Hero ───────────────────────────────────────────────
    st.markdown(f"""
    <div class="details-hero">
        <div class="details-hero-bg" style="{bg_style}"></div>
        <div class="details-hero-overlay"></div>
        <div class="details-hero-content">
            <div style="font-size:0.75rem;font-weight:800;letter-spacing:2px;color:#E50914;margin-bottom:0.5rem;text-transform:uppercase;">
                {genres_str}
            </div>
            <div style="font-size:clamp(2rem, 4vw, 3.2rem);font-weight:800;color:#FFFFFF;line-height:1.1;margin-bottom:0.8rem;">
                {short_title}
            </div>
            <div style="display:flex;align-items:center;gap:0.8rem;font-size:0.9rem;color:rgba(255,255,255,0.7);margin-bottom:0.5rem;">
                <span style="color:#FFD700;font-weight:700;">★ {tmdb_rating:.1f}</span>
                <span>•</span>
                <span>{year if year else "Classic"}</span>
                {f'<span>•</span><span>{runtime} min</span>' if runtime else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Main Content Grid: 30% Poster & Actions / 70% Insights & Plot ────────
    p_col, info_col = st.columns([3, 7], gap="large")

    with p_col:
        if poster_url:
            st.markdown(f'<img class="movie-poster-img" src="{poster_url}" style="border-radius:12px;border:1px solid rgba(255,255,255,0.1);box-shadow:0 15px 40px rgba(0,0,0,0.8);" alt="{short_title}">', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="width:100%;aspect-ratio:2/3;background:#181818;border-radius:12px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,0.08);color:#888;">
                <div style="text-align:center;padding:1rem;">{short_title}</div>
            </div>
            """, unsafe_allow_html=True)

        spacer("small")

        # Action Buttons
        is_fav = title in st.session_state.get("favorites", [])
        fav_label = "❤️ In Watchlist" if is_fav else "🤍 Add to Watchlist"
        if st.button(fav_label, key="btn_details_fav", use_container_width=True):
            favs = st.session_state.get("favorites", [])
            if title in favs:
                favs.remove(title)
                st.toast("Removed from watchlist.")
            else:
                favs.append(title)
                st.toast("Added to watchlist!", icon="❤️")
            st.session_state["favorites"] = favs
            st.rerun()

        if st.button("❮ Back to Catalog", key="btn_details_back", use_container_width=True):
            st.session_state["page"] = "Movies"
            st.rerun()

    with info_col:
        # Synopsis
        st.markdown(f"""
        <div style="margin-bottom:1.8rem;">
            <div class="section-eyebrow">SYNOPSIS</div>
            <div style="font-size:1rem;color:#D4D4D4;line-height:1.7;">{overview}</div>
        </div>
        """, unsafe_allow_html=True)

        # MovieLens Dataset Statistics
        m_id = movie_data.get("movieId")
        m_ratings = ratings[ratings["movieId"] == m_id]
        r_count = len(m_ratings)
        r_avg = m_ratings["rating"].mean() if r_count > 0 else 0.0

        st.markdown(f"""
        <div style="background:#141414;border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:1.2rem;margin-bottom:1.8rem;">
            <div style="font-size:0.7rem;font-weight:800;letter-spacing:2px;color:#E50914;margin-bottom:0.6rem;">MOVIELENS 1M STATS</div>
            <div style="display:flex;gap:2rem;font-size:0.85rem;color:#BBB;">
                <div>Total Community Ratings: <strong style="color:#FFF;">{r_count:,}</strong></div>
                <div>Community Average: <strong style="color:#FFD700;">★ {r_avg:.2f}</strong></div>
                <div>Internal ID: <strong style="color:#FFF;">#{m_id}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI Recommendation Insights & Similar Titles
        st.markdown("""
        <div class="section-eyebrow">AI SIMILARITY PROFILE</div>
        <div class="section-headline" style="font-size:1.3rem;margin-bottom:1rem;">More Like This</div>
        """, unsafe_allow_html=True)

        try:
            similar_df = hybrid_model.content_recommender.recommend(movie_title=title, n=4)
            if similar_df is not None and not similar_df.empty:
                render_movie_grid(
                    similar_df,
                    cols=4,
                    key_prefix="details_similar",
                    show_rank=False,
                    score_col="similarity_score",
                    show_actions=True,
                    fetch_tmdb=True,
                )
        except Exception as e:
            st.caption("Similar recommendations could not be computed.")

    spacer("large")
    render_footer()
