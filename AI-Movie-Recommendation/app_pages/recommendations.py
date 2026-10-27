"""
app_pages/recommendations.py
-----------------------------
CineAI Recommendations Page.

Layout:
    Left (70%): Recommendation results grid & AI score explanations
    Right (30%): AI Recommendation Engine controls
"""

from __future__ import annotations

import streamlit as st

from src import config
from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer
from src.components.model_loader import load_models, models_missing_error, try_recommend
from src.components.movie_card import (
    render_movie_card_with_actions,
    render_score_breakdown,
    strip_year,
    extract_year,
)

inject_global_css()
render_navbar("Recommendations")

# ── Load models ───────────────────────────────────────────────────────────────
movies, ratings, users, hybrid_model, collab_model, missing = load_models()

if missing:
    models_missing_error(missing)
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.8rem;">
    <div class="section-eyebrow">AI POWERED DISCOVERY</div>
    <div class="section-headline">Personalized Recommendations</div>
    <div class="section-subheadline">
        Fine-tune hybrid weighting between content similarity and collaborative intelligence.
    </div>
</div>
""", unsafe_allow_html=True)

# ── 70/30 Layout ──────────────────────────────────────────────────────────────
main_col, panel_col = st.columns([7, 3], gap="large")

# ════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — AI Engine Controls
# ════════════════════════════════════════════════════════════════════════════
with panel_col:
    st.markdown('<div class="ai-control-card">', unsafe_allow_html=True)
    st.markdown('<div class="ai-control-header">⚙ AI RECOMMENDATION ENGINE</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Recommendation Mode",
        options=["User Recommendations", "Similar Movies"],
        index=0 if st.session_state.get("rec_mode") != "Similar Movies" else 1,
        key="rec_mode_radio",
        label_visibility="collapsed",
    )
    is_user_mode = (mode == "User Recommendations")

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    n_recs = st.slider(
        "Number of recommendations",
        min_value=4,
        max_value=24,
        value=8,
        step=4,
        key="rec_count_slider",
    )

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    if is_user_mode:
        user_ids = sorted(ratings["userId"].unique().tolist())
        default_user_idx = 0
        if st.session_state.get("last_rec_user") in user_ids:
            default_user_idx = user_ids.index(st.session_state["last_rec_user"])

        selected_user = st.selectbox(
            "Target User Profile",
            user_ids,
            index=default_user_idx,
            key="rec_user_select",
            help="Select any of the 6,040 real MovieLens user profiles.",
        )
        selected_movie = None

        # Compact user profile
        user_ratings_df = ratings[ratings["userId"] == selected_user]
        n_ur = len(user_ratings_df)
        avg_ur = user_ratings_df["rating"].mean() if n_ur > 0 else 0.0
        has_cf = collab_model.has_sufficient_history(selected_user)

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
             border-radius:8px;padding:0.8rem;margin:0.8rem 0;">
            <div style="font-size:0.68rem;font-weight:700;letter-spacing:1.5px;color:#E50914;margin-bottom:0.4rem;">
                USER #{selected_user} STATS
            </div>
            <div style="font-size:0.8rem;color:#AAAAAA;line-height:1.7;">
                Total Ratings: <strong style="color:#FFFFFF;">{n_ur:,}</strong><br>
                Avg Score: <strong style="color:#FFD700;">★ {avg_ur:.2f}</strong><br>
                Engine Status: <strong style="color:{'#3FB950' if has_cf else '#F59E0B'};">
                    {'✓ Collaborative Active' if has_cf else '⚠️ Cold Start (Content Fallback)'}
                </strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:0.82rem;font-weight:700;color:#CCC;margin-bottom:0.3rem;'>Hybrid Weights</div>", unsafe_allow_html=True)
        content_weight = st.slider(
            "Content Weight (α)",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.get("content_weight_val", config.DEFAULT_CONTENT_WEIGHT)),
            step=0.05,
            key="slider_alpha",
            help="Higher α prioritizes genre similarity. Lower α prioritizes collaborative rating predictions.",
        )
        st.session_state["content_weight_val"] = content_weight
        collab_weight = round(1.0 - content_weight, 2)

        st.markdown(f"""
        <div style="font-size:0.75rem;color:#8A8A8A;margin-bottom:1rem;">
            Content (α): <strong style="color:#E50914;">{content_weight:.2f}</strong> &nbsp;•&nbsp; 
            Collab (β): <strong style="color:#58A6FF;">{collab_weight:.2f}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        movie_titles = sorted(movies["title"].tolist())
        default_movie_idx = 0
        if st.session_state.get("selected_movie") in movie_titles:
            default_movie_idx = movie_titles.index(st.session_state["selected_movie"])

        selected_movie = st.selectbox(
            "Select Base Movie",
            movie_titles,
            index=default_movie_idx,
            key="rec_movie_select",
        )
        selected_user = None
        content_weight = 1.0
        collab_weight = 0.0

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    run_btn = st.button(
        "⚡ GENERATE RECOMMENDATIONS" if is_user_mode else "🔍 FIND SIMILAR MOVIES",
        type="primary",
        key="execute_rec_btn",
        use_container_width=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LEFT MAIN — Results
# ════════════════════════════════════════════════════════════════════════════
with main_col:
    results_to_render = None
    is_fallback = False

    if run_btn:
        if is_user_mode:
            with st.spinner(f"Computing hybrid recommendations for User #{selected_user}..."):
                res, err = try_recommend(
                    hybrid_model.recommend_for_user,
                    user_id=selected_user,
                    n=n_recs,
                    content_weight=content_weight,
                    collaborative_weight=collab_weight,
                )
            if err:
                st.error(f"Error computing recommendations: {err}")
            elif res is not None and not res.empty:
                st.session_state["last_recommendations"] = res
                st.session_state["last_rec_user"] = selected_user
                results_to_render = res
        else:
            with st.spinner(f"Finding movies similar to '{strip_year(selected_movie)}'..."):
                res, err = try_recommend(
                    hybrid_model.recommend_similar_to_movie,
                    movie_title=selected_movie,
                    n=n_recs,
                )
            if err:
                st.error(f"Error finding similar movies: {err}")
            elif res is not None and not res.empty:
                st.session_state["last_recommendations"] = res
                st.session_state["last_rec_user"] = None
                results_to_render = res
    elif st.session_state.get("last_recommendations") is not None:
        results_to_render = st.session_state["last_recommendations"]

    if results_to_render is not None and not results_to_render.empty:
        if "fallback_used" in results_to_render.columns:
            is_fallback = bool(results_to_render["fallback_used"].iloc[0])

        if is_fallback and is_user_mode:
            st.markdown(f"""
            <div class="cold-start-box">
                <strong>⚠️ Cold-Start Profile:</strong> User #{selected_user} has limited ratings history.
                The system automatically applied pure content-based recommendation logic.
            </div>
            """, unsafe_allow_html=True)

        target_info = f"User #{selected_user}" if (is_user_mode and selected_user) else f'"{strip_year(selected_movie)}"' if selected_movie else "Your Selection"
        st.markdown(f"**Top {len(results_to_render)} Matches** for {target_info}")
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

        rec_cols = st.columns(4, gap="small")
        for i, (_, row) in enumerate(results_to_render.iterrows()):
            col = rec_cols[i % 4]
            with col:
                title = row.get("title", "")
                h_score = row.get("hybrid_score", row.get("content_score", None))
                c_score = row.get("content_score", None)
                cf_score = row.get("collaborative_score", None)

                render_movie_card_with_actions(
                    row_or_title=row,
                    idx_key=f"rec_res_{i}_{title[:8]}",
                    rank=i + 1,
                    hybrid_score=h_score,
                    content_score=c_score,
                    collaborative_score=cf_score,
                    fallback_used=is_fallback,
                )

                # Score breakdown in expander
                with st.expander("AI Score Breakdown", expanded=False):
                    render_score_breakdown(
                        content_score=c_score,
                        collaborative_score=cf_score,
                        hybrid_score=h_score,
                        fallback_used=is_fallback,
                    )
                    explanation = row.get("explanation", "")
                    if explanation:
                        st.caption(f"💡 {explanation}")

        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

        # Tabular Data Expander
        with st.expander("📊 View Raw Recommendation Data", expanded=False):
            disp_df = results_to_render.copy()
            st.dataframe(disp_df, use_container_width=True, hide_index=True)

    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#666;">
            <div style="font-size:3.5rem;margin-bottom:1rem;opacity:0.8;">🎬</div>
            <div style="font-size:1.3rem;font-weight:700;color:#FFF;margin-bottom:0.5rem;">
                Ready to Discover
            </div>
            <div style="font-size:0.88rem;color:#8A8A8A;max-width:400px;margin:0 auto;">
                Select a user profile or a base movie on the right panel, then click 
                <strong style="color:#E50914;">Generate Recommendations</strong> to run the hybrid engine.
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
render_footer()
