"""
app_pages/analytics.py
-----------------------
CineAI Analytics — Real MovieLens 1M statistics, rating distributions,
model evaluation benchmarks (RMSE, MAE, Precision@K, Recall@K), and architecture visualization.
"""

from __future__ import annotations

from collections import Counter
import pandas as pd
import streamlit as st

from src import config
from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer
from src.components.model_loader import load_models, load_metrics, models_missing_error

inject_global_css()
render_navbar("Analytics")

movies, ratings, users, hybrid_model, collab_model, missing = load_models()
if missing:
    models_missing_error(missing)
    st.stop()

metrics = load_metrics()
stats = metrics.get("dataset_stats") if metrics else None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.8rem;">
    <div class="section-eyebrow">METRICS & BENCHMARKS</div>
    <div class="section-headline">AI System Analytics</div>
    <div class="section-subheadline">
        Empirical evaluation results and statistical distributions from the MovieLens 1M dataset.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Dataset Stats ─────────────────────────────────────────────────────────────
if stats:
    n_movies = f"{stats['n_movies']:,}"
    n_users = f"{stats['n_users']:,}"
    n_ratings = f"{stats['n_ratings']:,}"
    avg_rating = f"{stats['avg_rating']:.2f}"
else:
    n_movies = f"{movies['movieId'].nunique():,}"
    n_users = f"{ratings['userId'].nunique():,}"
    n_ratings = f"{len(ratings):,}"
    avg_rating = f"{ratings['rating'].mean():.2f}"

c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{n_movies}</span>
        <span class="stat-card-tag">Movies Catalog</span>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{n_users}</span>
        <span class="stat-card-tag">Active Users</span>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{n_ratings}</span>
        <span class="stat-card-tag">Evaluated Ratings</span>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="stat-card-box">
        <span class="stat-card-num">{avg_rating}★</span>
        <span class="stat-card-tag">Dataset Average</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_insights, tab_eval = st.tabs(["📊 Dataset Insights", "⚡ Model Benchmarks"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1: Dataset Insights
# ════════════════════════════════════════════════════════════════════════════
with tab_insights:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    chart_c1, chart_c2 = st.columns(2, gap="large")

    with chart_c1:
        st.markdown("**Rating Value Distribution**")
        if stats and "rating_distribution" in stats:
            dist = stats["rating_distribution"]
            rdf = pd.DataFrame({
                "Stars": [f"{k} Stars" for k in sorted(dist.keys())],
                "Count": [dist[k] for k in sorted(dist.keys())],
            })
        else:
            vc = ratings["rating"].value_counts().sort_index()
            rdf = pd.DataFrame({
                "Stars": [f"{k:.0f} Stars" for k in vc.index],
                "Count": vc.values,
            })
        st.bar_chart(rdf.set_index("Stars"), color="#E50914", use_container_width=True)

    with chart_c2:
        st.markdown("**Top Genre Frequencies**")
        all_genres = []
        for g in movies["genres"].dropna():
            all_genres.extend(g.replace("|", " ").split())
        cnts = Counter(all_genres)
        gdf = pd.DataFrame(cnts.items(), columns=["Genre", "Count"]).sort_values("Count", ascending=False).head(10)
        st.bar_chart(gdf.set_index("Genre"), color="#58A6FF", use_container_width=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("**Most Rated Movies in the Dataset**")
    top_rated_counts = ratings.groupby("movieId")["rating"].count().reset_index()
    top_rated_counts.columns = ["movieId", "Rating Count"]
    top_rated_merged = top_rated_counts.sort_values("Rating Count", ascending=False).head(10).merge(movies, on="movieId")
    top_rated_merged["Title"] = top_rated_merged["title"].str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)
    st.bar_chart(top_rated_merged[["Title", "Rating Count"]].set_index("Title"), color="#3FB950", use_container_width=True)

    # Saved plots if available
    plots_dir = config.PLOTS_DIR
    plot_items = [
        ("rating_distribution.png", "Rating Distribution Breakdown"),
        ("ratings_per_movie.png", "Ratings per Movie Curve"),
        ("ratings_per_user.png", "Ratings per User Distribution"),
        ("top_rated_movies.png", "Top Rated Movies"),
    ]
    available_plots = [(f, c) for f, c in plot_items if (plots_dir / f).exists()]
    if available_plots:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("**Pre-Computed Dataset Visualizations**")
        pcols = st.columns(2, gap="medium")
        for idx, (f_name, caption) in enumerate(available_plots):
            with pcols[idx % 2]:
                st.image(str(plots_dir / f_name), caption=caption, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2: Model Benchmarks
# ════════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    if not metrics:
        st.info("Evaluation metrics have not been generated yet. Run `python train.py` to calculate model benchmarks.")
    else:
        st.markdown("**Model Performance Summary**")
        model_types = ["Content-Based", "Collaborative", "Hybrid"]
        m_colors = {"Content-Based": "#E50914", "Collaborative": "#58A6FF", "Hybrid": "#3FB950"}

        m_cols = st.columns(3, gap="medium")
        for col, m_name in zip(m_cols, model_types):
            m_data = metrics.get(m_name, {})
            rmse_val = m_data.get("rmse")
            mae_val = m_data.get("mae")
            p5_val = m_data.get("precision_at_5")
            p10_val = m_data.get("precision_at_10")
            r5_val = m_data.get("recall_at_5")
            r10_val = m_data.get("recall_at_10")

            rmse_txt = f"{rmse_val:.4f}" if isinstance(rmse_val, (int, float)) else "N/A (Ranking)"
            mae_txt = f"{mae_val:.4f}" if isinstance(mae_val, (int, float)) else "N/A"
            p5_txt = f"{p5_val:.4f}" if isinstance(p5_val, (int, float)) else "N/A"
            p10_txt = f"{p10_val:.4f}" if isinstance(p10_val, (int, float)) else "N/A"
            r5_txt = f"{r5_val:.4f}" if isinstance(r5_val, (int, float)) else "N/A"
            r10_txt = f"{r10_val:.4f}" if isinstance(r10_val, (int, float)) else "N/A"

            c_hex = m_colors.get(m_name, "#E50914")

            with col:
                st.markdown(f"""
                <div style="background:#141414;border:1px solid {c_hex}44;border-radius:12px;padding:1.4rem;">
                    <div style="font-size:0.75rem;font-weight:800;letter-spacing:1.5px;color:{c_hex};margin-bottom:0.8rem;">
                        {m_name.upper()}
                    </div>
                    <div style="font-size:0.82rem;color:#AAA;line-height:1.9;">
                        <div>RMSE: <strong style="color:#FFF;">{rmse_txt}</strong></div>
                        <div>MAE: <strong style="color:#FFF;">{mae_txt}</strong></div>
                        <div>Precision@5: <strong style="color:#FFF;">{p5_txt}</strong></div>
                        <div>Precision@10: <strong style="color:#FFF;">{p10_txt}</strong></div>
                        <div>Recall@5: <strong style="color:#FFF;">{r5_txt}</strong></div>
                        <div>Recall@10: <strong style="color:#FFF;">{r10_txt}</strong></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("**Comparative Evaluation Table**")

        comp_rows = []
        for m_name in model_types:
            m_data = metrics.get(m_name, {})
            comp_rows.append({
                "Model": m_name,
                "RMSE": m_data.get("rmse", "N/A"),
                "MAE": m_data.get("mae", "N/A"),
                "Precision@5": m_data.get("precision_at_5", "N/A"),
                "Recall@5": m_data.get("recall_at_5", "N/A"),
                "Precision@10": m_data.get("precision_at_10", "N/A"),
                "Recall@10": m_data.get("recall_at_10", "N/A"),
            })
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

        # Plot images
        model_plots = [
            ("model_comparison.png", "Error Metrics Comparison"),
            ("precision_at_k_comparison.png", "Precision @ K Comparison"),
            ("recall_at_k_comparison.png", "Recall @ K Comparison"),
        ]
        avail_m_plots = [(f, c) for f, c in model_plots if (plots_dir / f).exists()]
        if avail_m_plots:
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            st.markdown("**Benchmark Visualizations**")
            bench_cols = st.columns(len(avail_m_plots), gap="medium")
            for i, (fn, cap) in enumerate(avail_m_plots):
                with bench_cols[i]:
                    st.image(str(plots_dir / fn), caption=cap, use_container_width=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
render_footer()
