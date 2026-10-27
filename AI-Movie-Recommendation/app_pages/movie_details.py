"""
app_pages/movie_details.py
---------------------------
CineAI Movie Details — Full-page cinematic overview with backdrop,
metadata, TMDB enrichment, AI similarity profile, and "More Like This" recommendations.
"""

from __future__ import annotations

import streamlit as st

from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer
from src.components.model_loader import load_models, models_missing_error, try_recommend
from src.components.movie_card import (
    render_movie_card_with_actions,
    strip_year,
    extract_year,
    format_genres_html,
)
from src.tmdb import get_enriched_movie, format_runtime

inject_global_css()
render_navbar("Movie Details")

movies, ratings, users, hybrid_model, collab_model, missing = load_models()
if missing:
    models_missing_error(missing)
    st.stop()

# ── Check Selected Movie ──────────────────────────────────────────────────────
selected_title = st.session_state.get("selected_movie_detail")

if not selected_title:
    # Default fallback to Godfather if directly navigated
    selected_title = "The Godfather (1972)"

# Add to recently viewed
if "recently_viewed" not in st.session_state:
    st.session_state["recently_viewed"] = []
if selected_title not in st.session_state["recently_viewed"]:
    st.session_state["recently_viewed"].insert(0, selected_title)
    st.session_state["recently_viewed"] = st.session_state["recently_viewed"][:20]

# Lookup movie in dataframe
movie_row = movies[movies["title"] == selected_title]
if movie_row.empty:
    st.error(f"Movie '{selected_title}' not found in database.")
    st.stop()

movie_data = movie_row.iloc[0]
clean_title = strip_year(selected_title)
year = extract_year(selected_title)
genres_raw = movie_data.get("genres", "")

# ── TMDB Enrichment ───────────────────────────────────────────────────────────
tmdb_info = {}
try:
    tmdb_info = get_enriched_movie(selected_title)
except Exception:
    pass

backdrop_url = tmdb_info.get("backdrop_url")
poster_url = tmdb_info.get("poster_url")
overview = tmdb_info.get("overview") or "No detailed overview available for this title in TMDB."
tmdb_rating = tmdb_info.get("tmdb_rating")
runtime_min = tmdb_info.get("runtime")
formatted_runtime = format_runtime(runtime_min) if runtime_min else ""

# ── Back Navigation Button ────────────────────────────────────────────────────
btn_col1, _ = st.columns([2, 8])
with btn_col1:
    if st.button("← Back to Browse", key="back_from_details_btn"):
        st.session_state["page"] = "Search"
        st.rerun()

st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

# ── Hero Banner with Backdrop ─────────────────────────────────────────────────
backdrop_style = f'background-image: url("{backdrop_url}");' if backdrop_url else 'background: radial-gradient(circle at 80% 20%, #2b0c0c 0%, #121212 80%);'

st.markdown(f"""
<div class="details-hero">
    <div class="details-hero-bg" style="{backdrop_style}"></div>
    <div class="details-hero-overlay"></div>
    <div class="details-hero-content">
        <div class="hero-badge">NOW VIEWING</div>
        <div style="font-size:clamp(2rem, 4vw, 3.2rem);font-weight:800;color:#FFF;line-height:1.1;margin-bottom:0.5rem;text-shadow:0 4px 20px rgba(0,0,0,0.8);">
            {clean_title}
        </div>
        <div style="font-size:0.9rem;color:rgba(255,255,255,0.7);display:flex;gap:0.8rem;align-items:center;flex-wrap:wrap;">
            <span>{year}</span>
            {f'<span>•</span><span>{formatted_runtime}</span>' if formatted_runtime else ''}
            {f'<span>•</span><span style="color:#FFD700;font-weight:700;">★ {tmdb_rating:.1f} TMDB</span>' if tmdb_rating else ''}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Details Layout ────────────────────────────────────────────────────────────
d_left, d_right = st.columns([1, 2.5], gap="large")

with d_left:
    if poster_url:
        st.markdown(f"""
        <img src="{poster_url}" alt="{clean_title}" style="width:100%;border-radius:12px;box-shadow:0 15px 40px rgba(0,0,0,0.7);border:1px solid rgba(255,255,255,0.08);margin-bottom:1.2rem;">
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="width:100%;aspect-ratio:2/3;background:#181818;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:3rem;color:#444;border:1px solid rgba(255,255,255,0.08);margin-bottom:1.2rem;">
            🎬
        </div>
        """, unsafe_allow_html=True)

    # MovieLens rating metric
    movie_id = movie_data.get("movieId")
    movie_ratings = ratings[ratings["movieId"] == movie_id]
    if not movie_ratings.empty:
        ml_avg = movie_ratings["rating"].mean()
        ml_count = len(movie_ratings)
        st.markdown(f"""
        <div class="stat-card-box" style="margin-bottom:1rem;">
            <span class="stat-card-num" style="color:#FFD700;">★ {ml_avg:.2f}</span>
            <span class="stat-card-tag">MovieLens ({ml_count:,} ratings)</span>
        </div>
        """, unsafe_allow_html=True)

with d_right:
    # Genres & Overview
    genres_formatted = format_genres_html(genres_raw, max_genres=6)
    st.markdown(f"""
    <div style="margin-bottom:1.2rem;">
        <div style="font-size:0.7rem;font-weight:800;letter-spacing:2px;color:#E50914;margin-bottom:0.4rem;">GENRES</div>
        <div>{genres_formatted}</div>
    </div>
    <div style="margin-bottom:1.5rem;">
        <div style="font-size:0.7rem;font-weight:800;letter-spacing:2px;color:#E50914;margin-bottom:0.4rem;">SYNOPSIS</div>
        <div style="font-size:0.95rem;line-height:1.7;color:#D0D0D0;">{overview}</div>
    </div>
    """, unsafe_allow_html=True)

    # Actions: Favorites & Similar
    act_c1, act_c2 = st.columns([1.5, 2], gap="small")
    with act_c1:
        is_fav = selected_title in st.session_state.get("favorites", [])
        fav_label = "Remove from Favorites" if is_fav else "Add to Favorites"
        fav_icon = "💔" if is_fav else "❤️"
        if st.button(f"{fav_icon} {fav_label}", key="details_fav_btn", use_container_width=True):
            if is_fav:
                st.session_state["favorites"].remove(selected_title)
                st.toast(f"Removed '{clean_title}' from favorites")
            else:
                st.session_state["favorites"].append(selected_title)
                st.toast(f"Added '{clean_title}' to favorites! ❤️")
            st.rerun()

    with act_c2:
        if st.button("⚡ Find Similar Recommendations", key="details_rec_similar_btn", type="primary", use_container_width=True):
            st.session_state["selected_movie"] = selected_title
            st.session_state["rec_mode"] = "Similar Movies"
            st.session_state["page"] = "Recommendations"
            st.rerun()

    # Content Similarity Insights
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">AI PROFILE</div>
    <div class="section-headline" style="font-size:1.3rem;">Recommendation Intelligence</div>
    """, unsafe_allow_html=True)

    try:
        sim_matrix = hybrid_model.content_model.similarity_matrix
        idx = hybrid_model.content_model._id_to_index.get(movie_id)
        if idx is not None:
            sims = sim_matrix[idx]
            pos_sims = sims[sims > 0]
            avg_sim = float(pos_sims.mean()) if len(pos_sims) > 0 else 0.0
            max_sim = float(sims.max()) if len(sims) > 0 else 0.0

            st.markdown(f"""
            <div style="background:#141414;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:1.2rem;margin-top:0.8rem;">
                <div class="score-metric-row">
                    <div class="score-metric-header">
                        <span class="score-metric-label">Average TF-IDF Genre Similarity across catalog</span>
                        <span class="score-metric-val">{int(avg_sim*100)}%</span>
                    </div>
                    <div class="score-metric-track">
                        <div class="score-metric-fill" style="width:{int(avg_sim*100)}%;background:linear-gradient(90deg,#E50914,#FF6B6B);"></div>
                    </div>
                </div>
                <div class="score-metric-row" style="margin-bottom:0;">
                    <div class="score-metric-header">
                        <span class="score-metric-label">Max Feature Overlap with Nearest Neighbor</span>
                        <span class="score-metric-val">{int(max_sim*100)}%</span>
                    </div>
                    <div class="score-metric-track">
                        <div class="score-metric-fill" style="width:{int(max_sim*100)}%;background:linear-gradient(90deg,#3FB950,#56D364);"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ── More Like This (Content Similarity) ───────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">MORE LIKE THIS</div>
<div class="section-headline">Related Movies</div>
<div class="section-subheadline">Nearest neighbors identified via cosine similarity on TF-IDF genre vectors.</div>
""", unsafe_allow_html=True)

with st.spinner("Finding similar titles..."):
    similar_df, err = try_recommend(
        hybrid_model.recommend_similar_to_movie,
        movie_title=selected_title,
        n=5,
    )

if not err and similar_df is not None and not similar_df.empty:
    sim_cols = st.columns(5, gap="small")
    for i, (_, row) in enumerate(similar_df.iterrows()):
        col = sim_cols[i % 5]
        with col:
            t = row.get("title", "")
            c_score = row.get("content_score", None)
            render_movie_card_with_actions(
                row_or_title=row,
                idx_key=f"details_sim_{i}_{t[:8]}",
                rank=i + 1,
                hybrid_score=c_score,
            )
else:
    st.caption("No related movies could be retrieved.")

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
render_footer()
