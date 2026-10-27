"""
app_pages/favorites.py
-----------------------
CineAI Favorites — User's personal saved watchlist and browsing history.
"""

from __future__ import annotations

import streamlit as st

from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer
from src.components.model_loader import load_models, models_missing_error
from src.components.movie_card import render_movie_card_with_actions, strip_year

inject_global_css()
render_navbar("Favorites")

movies, ratings, users, hybrid_model, collab_model, missing = load_models()
if missing:
    models_missing_error(missing)
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.8rem;">
    <div class="section-eyebrow">SAVED TITLES</div>
    <div class="section-headline">My Watchlist</div>
    <div class="section-subheadline">
        Movies you have saved for later discovery and viewing.
    </div>
</div>
""", unsafe_allow_html=True)

favorites = st.session_state.get("favorites", [])

if not favorites:
    st.markdown("""
    <div style="text-align:center;padding:4rem 1rem;color:#666;">
        <div style="font-size:3.5rem;margin-bottom:1rem;color:#E50914;opacity:0.8;">❤️</div>
        <div style="font-size:1.4rem;font-weight:700;color:#FFF;margin-bottom:0.5rem;">
            Your Watchlist is Empty
        </div>
        <div style="font-size:0.88rem;color:#8A8A8A;max-width:420px;margin:0 auto 1.5rem;">
            Discover movies across our recommendations and catalog, then click the heart icon to save them here.
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_e1, btn_e2 = st.columns([1, 1])
    with btn_e1:
        if st.button("⚡ Get Recommendations", key="fav_empty_rec", type="primary", use_container_width=True):
            st.session_state["page"] = "Recommendations"
            st.rerun()
    with btn_e2:
        if st.button("🔍 Explore Movies", key="fav_empty_exp", type="secondary", use_container_width=True):
            st.session_state["page"] = "Search"
            st.rerun()

else:
    head_c1, head_c2 = st.columns([3, 1])
    with head_c1:
        st.markdown(f"**{len(favorites)} saved movies** in your watchlist")
    with head_c2:
        if st.button("🗑️ Clear All", key="clear_all_favs_btn", use_container_width=True):
            st.session_state["favorites"] = []
            st.rerun()

    st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

    fav_cols = st.columns(5, gap="small")
    for i, title in enumerate(favorites):
        col = fav_cols[i % 5]
        with col:
            match = movies[movies["title"] == title]
            row = match.iloc[0] if not match.empty else {"title": title, "genres": ""}
            render_movie_card_with_actions(
                row_or_title=row,
                idx_key=f"fav_list_{i}_{title[:8]}",
            )

# ── Recently Viewed Section ───────────────────────────────────────────────────
recently_viewed = st.session_state.get("recently_viewed", [])
if recently_viewed:
    st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-eyebrow">SESSION HISTORY</div>
    <div class="section-headline">Recently Viewed</div>
    """, unsafe_allow_html=True)

    rv_head1, rv_head2 = st.columns([3, 1])
    with rv_head2:
        if st.button("Clear History", key="clear_history_btn", use_container_width=True):
            st.session_state["recently_viewed"] = []
            st.rerun()

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    recent_cols = st.columns(5, gap="small")
    for i, title in enumerate(recently_viewed[:5]):
        col = recent_cols[i % 5]
        with col:
            match = movies[movies["title"] == title]
            row = match.iloc[0] if not match.empty else {"title": title, "genres": ""}
            render_movie_card_with_actions(
                row_or_title=row,
                idx_key=f"recent_{i}_{title[:8]}",
            )

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
render_footer()
