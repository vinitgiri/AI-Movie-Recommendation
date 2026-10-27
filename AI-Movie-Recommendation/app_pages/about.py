"""
app_pages/about.py
-------------------
CineAI About Page — Project Architecture, ML Methodologies, and Technical Documentation.
"""

from __future__ import annotations

import streamlit as st

from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer, get_cineai_logo_html

inject_global_css()
render_navbar("About")

# ── Hero ──────────────────────────────────────────────────────────────────────
logo_large = get_cineai_logo_html(size="large")

st.markdown(f"""
<div style="text-align:center;padding:2.5rem 1rem 1.5rem;">
    <div style="display:inline-flex;justify-content:center;margin-bottom:1.2rem;">
        {logo_large}
    </div>
    <div style="font-size:clamp(1.8rem, 3.5vw, 2.6rem);font-weight:800;color:#FFFFFF;letter-spacing:-1px;line-height:1.2;margin-bottom:1rem;">
        AI-Based Personalized Movie<br><span style="color:#E50914;">Recommendation System</span>
    </div>
    <div style="font-size:0.95rem;color:#A0A0A0;max-width:680px;margin:0 auto;line-height:1.6;">
        A high-performance hybrid recommendation engine combining TF-IDF content similarity 
        with SVD collaborative matrix factorization trained on the MovieLens 1M benchmark.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Problem & Solution ────────────────────────────────────────────────────────
p_col1, p_col2 = st.columns(2, gap="large")

with p_col1:
    st.markdown("""
    <div style="background:#141414;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:1.6rem;height:100%;">
        <div style="font-size:0.72rem;font-weight:800;letter-spacing:2px;color:#E50914;margin-bottom:0.8rem;">THE PROBLEM</div>
        <div style="font-size:1.1rem;font-weight:700;color:#FFF;margin-bottom:0.8rem;">Single-Model Limitations</div>
        <div style="font-size:0.85rem;color:#AAA;line-height:1.7;">
            Traditional recommendation algorithms suffer from structural bottlenecks when deployed independently:
            <ul style="margin-top:0.5rem;padding-left:1.2rem;">
                <li><strong>Pure Content-Based:</strong> Struggles with over-specialization and ignores cross-user collective intelligence.</li>
                <li><strong>Pure Collaborative Filtering:</strong> Crippled by the cold-start problem when dealing with new or sparse user profiles.</li>
                <li><strong>Unweighted Approaches:</strong> Fail to adapt dynamically to diverse user interaction frequencies.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

with p_col2:
    st.markdown("""
    <div style="background:#141414;border:1px solid rgba(63,185,80,0.3);border-radius:12px;padding:1.6rem;height:100%;">
        <div style="font-size:0.72rem;font-weight:800;letter-spacing:2px;color:#3FB950;margin-bottom:0.8rem;">THE SOLUTION</div>
        <div style="font-size:1.1rem;font-weight:700;color:#FFF;margin-bottom:0.8rem;">Weighted Hybrid AI Fusion</div>
        <div style="font-size:0.85rem;color:#AAA;line-height:1.7;">
            Our hybrid architecture harmonizes both approaches through a unified scoring pipeline:
            <ul style="margin-top:0.5rem;padding-left:1.2rem;">
                <li><strong>TF-IDF Vector Space:</strong> Computes high-dimensional cosine similarities across genre features.</li>
                <li><strong>SVD Latent Factorization:</strong> Extracts 100 latent preferences from 1,000,209 ratings across 6,040 users.</li>
                <li><strong>Score Normalization & Fusion:</strong> Scales disparate score spaces to [0, 1] with automatic cold-start fallback.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">TECH STACK</div>
<div class="section-headline">Engineering & Frameworks</div>
""", unsafe_allow_html=True)

TECH_ITEMS = [
    ("🐍", "Python 3.10+", "Core Language"),
    ("⚡", "Streamlit", "Cinematic UI"),
    ("🧠", "Scikit-Learn", "TF-IDF & Cosine Sim"),
    ("⭐", "Scikit-Surprise", "SVD Matrix Factorization"),
    ("🐼", "Pandas & NumPy", "Data Pipelines"),
    ("🎬", "MovieLens 1M", "1M+ Ratings Dataset"),
    ("🌐", "TMDB API", "Metadata & Artworks"),
    ("📊", "Matplotlib / Seaborn", "Evaluation Plots"),
]

tcols = st.columns(4, gap="small")
for i, (ico, name, sub) in enumerate(TECH_ITEMS):
    with tcols[i % 4]:
        st.markdown(f"""
        <div class="stat-card-box" style="padding:1rem;margin-bottom:0.8rem;">
            <div style="font-size:1.6rem;margin-bottom:0.3rem;">{ico}</div>
            <div style="font-size:0.85rem;font-weight:700;color:#FFF;">{name}</div>
            <div style="font-size:0.7rem;color:#888;">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 3.5rem;'></div>", unsafe_allow_html=True)

# ── Mathematical Formulation ──────────────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">FORMULATION</div>
<div class="section-headline">Hybrid Scoring Formula</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,rgba(229,9,20,0.06),rgba(88,166,255,0.06));border:1px solid rgba(229,9,20,0.3);border-radius:12px;padding:1.8rem;text-align:center;">
    <div style="font-size:1.15rem;font-weight:800;color:#FFF;margin-bottom:0.8rem;font-family:monospace;">
        Score<sub>hybrid</sub>(u, m) = α · Norm(Score<sub>content</sub>(u, m)) + β · Norm(Score<sub>collab</sub>(u, m))
    </div>
    <div style="font-size:0.85rem;color:#BBB;max-width:700px;margin:0 auto;line-height:1.6;">
        Where α + β = 1.0. When a user profile has fewer than 5 historical ratings, the engine 
        automatically sets α = 1.0 and β = 0.0 (Cold-Start Content Fallback) to guarantee 
        zero recommendation disruption.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
render_footer()
