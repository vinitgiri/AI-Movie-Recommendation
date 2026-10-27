"""
src/ui/recommendations.py
-------------------------
CineAI Recommendations Page — 70/30 layout with interactive AI controls,
weight tuning, user profile inspection, cold-start handling, and score breakdowns.
"""

from __future__ import annotations

import streamlit as st
import re

from src.profile import initialize_profile_state, preferences

from src.ui.styles import inject_global_css
from src.ui.navigation import render_navbar, render_footer
from src.ui.components import (
    render_section_header,
    render_movie_grid,
    render_score_bars,
    render_empty_state,
    spacer,
)
from src.components.model_loader import load_models, models_missing_error, try_recommend


def _apply_profile_filters(results):
    """Apply profile filters that map to fields exposed by the ML result.

    Filters must never reduce a non-empty result set to zero rows: if a
    preference window cannot match the catalog (for example a year range
    newer than any MovieLens title), that filter is skipped instead.
    """
    if results is None or len(results) == 0:
        return results

    prefs = preferences()
    filtered = results.copy()
    include = prefs.get("include_genres", [])
    exclude = prefs.get("exclude_genres", [])
    if include:
        filtered = filtered[filtered["genres"].apply(lambda value: any(g.lower() in str(value).lower() for g in include))]
    if exclude:
        filtered = filtered[filtered["genres"].apply(lambda value: not any(g.lower() in str(value).lower() for g in exclude))]

    def year_for(title):
        match = re.search(r"\((\d{4})\)", str(title))
        return int(match.group(1)) if match else None

    from_year = int(prefs.get("from_year", 1900))
    to_year = int(prefs.get("to_year", 2100))
    years = filtered["title"].apply(year_for)
    known_years = years.dropna()
    if len(known_years) > 0:
        data_from = int(known_years.min())
        data_to = int(known_years.max())
        # Only apply the year window when it overlaps the catalog range.
        if from_year <= data_to and to_year >= data_from:
            filtered = filtered[years.isna() | years.between(from_year, to_year)]
    minimum_rating = float(prefs.get("minimum_rating", 0.0))
    if minimum_rating > 0 and "predicted_rating" in filtered.columns:
        filtered = filtered[filtered["predicted_rating"] >= minimum_rating]
    threshold = float(prefs.get("similarity_threshold", 0.0))
    score_column = "content_score" if "content_score" in filtered.columns else "hybrid_score"
    if threshold > 0 and score_column in filtered.columns:
        filtered = filtered[filtered[score_column] >= threshold]

    if filtered.empty and not results.empty:
        return results
    return filtered


def _friendly_error(err: str) -> str:
    """Map known recommender exceptions to actionable user-facing guidance."""
    message = str(err)
    if "Unknown userId" in message:
        return "No rating history found for this User ID. Try a User ID between 1 and 6040."
    return message


def render():
    """Render the AI Recommendations experience."""
    inject_global_css()
    render_navbar("Recommendations")

    movies, ratings, users, hybrid_model, collab_model, missing = load_models()
    if missing:
        models_missing_error(missing)
        st.stop()

    render_section_header(
        "AI ENGINE",
        "Your Personalized Recommendations",
        "Fine-tune hybrid weighting between content similarity and latent collaborative factorization.",
    )
    initialize_profile_state()
    profile_prefs = preferences()

    # 70% Left Recommendations / 30% Right AI Controls
    recs_col, ctrl_col = st.columns([7, 3], gap="large")

    with ctrl_col:
        st.markdown('<div class="ai-control-card">', unsafe_allow_html=True)
        st.markdown('<div class="ai-control-header">AI RECOMMENDATION ENGINE</div>', unsafe_allow_html=True)

        mode_options = ["Hybrid Fusion (User Profile)", "Content Similarity (Movie)", "Collaborative Filtering"]
        pref_to_option = {
            "Hybrid Fusion": mode_options[0],
            "Hybrid Fusion (User Profile)": mode_options[0],
            "Content Similarity": mode_options[1],
            "Content Similarity (Movie)": mode_options[1],
            "Collaborative Filtering": mode_options[2],
        }
        saved_mode = str(profile_prefs.get("mode", "Hybrid Fusion"))
        mode = st.radio(
            "Recommendation Strategy",
            mode_options,
            index=mode_options.index(pref_to_option.get(saved_mode, mode_options[0])),
            label_visibility="collapsed",
        )

        st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)

        if "Hybrid" in mode:
            user_id = st.number_input(
                "User ID (1 – 6,040)",
                min_value=1,
                max_value=6040,
                value=int(st.session_state.get("selected_user_id", 1)),
                step=1,
            )
            st.session_state["selected_user_id"] = user_id

            # User profile stats
            u_ratings = ratings[ratings["userId"] == user_id]
            u_count = len(u_ratings)
            u_avg = u_ratings["rating"].mean() if u_count > 0 else 0.0

            st.markdown(f"""
            <div style="background:#1C1C1C;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:0.75rem;margin-bottom:1rem;font-size:0.78rem;">
                <div style="color:#888;margin-bottom:0.2rem;">PROFILE INSIGHTS:</div>
                <div style="color:#FFF;"><strong>{u_count}</strong> ratings submitted · <strong>{u_avg:.2f}★</strong> average</div>
            </div>
            """, unsafe_allow_html=True)

            stored_alpha = float(profile_prefs.get("alpha", st.session_state.get("alpha_weight", 0.5)))
            alpha = st.slider(
                "Content Weight (α)",
                min_value=0.0,
                max_value=1.0,
                value=max(0.0, min(1.0, stored_alpha)),
                step=0.05,
                help="Weight assigned to TF-IDF genre text similarity.",
            )
            alpha = max(0.0, min(1.0, float(alpha)))
            st.session_state["alpha_weight"] = alpha
            beta = round(1.0 - alpha, 2)

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#888;margin-top:-0.5rem;margin-bottom:1rem;">
                <span>Content: <strong style="color:#E50914;">{int(alpha*100)}%</strong></span>
                <span>Collab: <strong style="color:#58A6FF;">{int(beta*100)}%</strong></span>
            </div>
            """, unsafe_allow_html=True)

            n_recs = st.slider("Number of Recommendations", 5, 30, int(profile_prefs.get("recommendation_count", 10)), step=5)

            compute_btn = st.button("Generate Recommendations", type="primary", use_container_width=True)

        elif "Content" in mode:
            # Content-based on single movie
            all_titles = sorted(movies["title"].dropna().unique().tolist())
            default_idx = 0
            if "Godfather, The (1972)" in all_titles:
                default_idx = all_titles.index("Godfather, The (1972)")

            movie_choice = st.selectbox("Select Seed Movie", all_titles, index=default_idx)
            n_recs = st.slider("Number of Similar Titles", 5, 20, 10, step=5)
            compute_btn = st.button("Find Similar Movies", type="primary", use_container_width=True)

        else:
            n_recs = st.slider("Number of Recommendations", 5, 30, int(profile_prefs.get("recommendation_count", 10)), step=5)
            compute_btn = st.button("Generate Collaborative Recommendations", type="primary", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with recs_col:
        if "Hybrid" in mode:
            user_id = st.session_state.get("selected_user_id", 1)
            alpha = st.session_state.get("alpha_weight", 0.5)

            recs, err = try_recommend(
                hybrid_model.recommend_for_user,
                user_id=user_id,
                n=n_recs,
                content_weight=alpha,
                collaborative_weight=1.0 - alpha,
            )

            if err:
                render_empty_state("⚠️", "Recommendation Error", _friendly_error(err))
            elif recs is not None and not recs.empty:
                recs = _apply_profile_filters(recs)
                st.markdown(f"""
                <div style="font-size:0.85rem;color:#AAA;margin-bottom:0.8rem;">
                    Displaying <strong>{len(recs)}</strong> tailored titles for User #{user_id}
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="rec-grid-anchor"></div>', unsafe_allow_html=True)
                render_movie_grid(
                    recs,
                    cols=4,
                    key_prefix="rec_grid",
                    show_rank=True,
                    score_col="hybrid_score",
                    show_actions=True,
                    fetch_tmdb=True,
                )

                # Score breakdown expander
                with st.expander("🔬 View Detailed Score Breakdown", expanded=False):
                    for _, row in recs.head(5).iterrows():
                        st.markdown(f"**{row['title']}**")
                        render_score_bars(
                            content_score=row.get("content_score"),
                            collaborative_score=row.get("collaborative_score"),
                            hybrid_score=row.get("hybrid_score"),
                            fallback_used=row.get("fallback_used", False),
                        )
                        st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:0.8rem 0;'>", unsafe_allow_html=True)

            else:
                render_empty_state(
                    "🎬",
                    "No recommendations available for this user yet.",
                    "Try another User ID or switch recommendation mode.",
                )

        elif "Content" in mode:
            # Content based
            recs, err = try_recommend(
                hybrid_model.content_model.recommend,
                movie_title=movie_choice,
                n=n_recs,
            )

            if err:
                render_empty_state("⚠️", "Content Recommendation Error", _friendly_error(err))
            elif recs is not None and not recs.empty:
                recs = _apply_profile_filters(recs)
                st.markdown(f"""
                <div style="font-size:0.85rem;color:#AAA;margin-bottom:0.8rem;">
                    Displaying <strong>{len(recs)}</strong> titles similar in genre & themes to <em>{movie_choice}</em>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="rec-grid-anchor"></div>', unsafe_allow_html=True)
                render_movie_grid(
                    recs,
                    cols=4,
                    key_prefix="content_rec_grid",
                    show_rank=True,
                    score_col="content_score",
                    show_actions=True,
                    fetch_tmdb=True,
                )
            else:
                render_empty_state(
                    "🎬",
                    "No recommendations available yet.",
                    "Try another seed movie or switch recommendation mode.",
                )
        else:
            user_id = st.session_state.get("selected_user_id", 1)
            recs, err = try_recommend(collab_model.recommend, user_id=user_id, n=n_recs)
            if err:
                render_empty_state("⚠️", "Recommendation Error", _friendly_error(err))
            elif recs is not None and not recs.empty:
                st.markdown(f"""
                <div style="font-size:0.85rem;color:#AAA;margin-bottom:0.8rem;">
                    Displaying <strong>{len(recs)}</strong> collaborative recommendations for User #{user_id}
                </div>
                """, unsafe_allow_html=True)
                recs = recs.copy()
                recs["ai_score"] = (recs["predicted_rating"].astype(float) / 5.0).clip(0.0, 1.0)
                st.markdown('<div class="rec-grid-anchor"></div>', unsafe_allow_html=True)
                render_movie_grid(recs, cols=4, key_prefix="collab_grid", show_rank=True, score_col="ai_score", show_actions=True, fetch_tmdb=True)
            else:
                render_empty_state(
                    "🎬",
                    "No recommendations available for this user yet.",
                    "Try another User ID or switch recommendation mode.",
                )

    spacer("large")
    render_footer()
