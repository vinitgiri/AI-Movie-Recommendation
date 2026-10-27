"""
src/components/styles.py
-----------------------
Comprehensive cinematic dark CSS injected via st.markdown for CineAI.
Pure CSS styling — ZERO visible raw HTML artifacts.
"""

from __future__ import annotations

import streamlit as st


def inject_global_css():
    """Inject global CSS rules to create a full-screen, cinematic dark UI."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cinzel:wght@700;900&display=swap');

    /* ── Reset & Base ────────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0a0a0a !important;
        color: #F5F5F5 !important;
    }

    /* Hide standard Streamlit header & sidebar navigation to ensure full-screen cinematic feel */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        z-index: 0 !important;
    }
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
    }

    /* Container Full Viewport Width */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1500px !important;
        margin: 0 auto !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        overflow-x: hidden;
        padding-top: 0.5rem !important;
    }

    /* ── Sticky Navbar ───────────────────────────────────────────────────── */
    .cineai-navbar-container {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(10, 10, 10, 0.92);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.6rem 0.5rem;
        margin-bottom: 1.5rem;
        border-radius: 0 0 12px 12px;
    }

    .cineai-brand {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        font-weight: 900;
        letter-spacing: 1px;
        color: #FFFFFF;
        text-shadow: 0 0 12px rgba(229, 9, 20, 0.4);
    }
    .cineai-brand .red-dot {
        width: 8px;
        height: 8px;
        background-color: #E50914;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #E50914;
    }
    .cineai-brand .accent {
        color: #E50914;
    }

    /* ── Native Streamlit Button Styling ─────────────────────────────────── */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
        padding: 0.4rem 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: #141414 !important;
        color: #E0E0E0 !important;
    }

    .stButton > button:hover {
        background: #222222 !important;
        border-color: rgba(229, 9, 20, 0.5) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(229, 9, 20, 0.15);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #E50914 0%, #B80710 100%) !important;
        border: 1px solid #E50914 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.35) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #F40612 0%, #CC0812 100%) !important;
        box-shadow: 0 6px 20px rgba(229, 9, 20, 0.5) !important;
        transform: translateY(-2px);
    }

    /* ── Hero Section ────────────────────────────────────────────────────── */
    .hero-banner {
        position: relative;
        width: 100%;
        min-height: 72vh;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 2.5rem;
        display: flex;
        align-items: center;
        background-color: #0e0e0e;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
    }

    .hero-bg-layer {
        position: absolute;
        inset: 0;
        z-index: 1;
        background-size: cover;
        background-position: center top;
        background-repeat: no-repeat;
    }

    .hero-gradient-overlay {
        position: absolute;
        inset: 0;
        z-index: 2;
        background: linear-gradient(
            to right,
            rgba(10, 10, 10, 0.95) 0%,
            rgba(10, 10, 10, 0.85) 35%,
            rgba(10, 10, 10, 0.4) 70%,
            rgba(10, 10, 10, 0.1) 100%
        ),
        linear-gradient(
            to top,
            rgba(10, 10, 10, 0.98) 0%,
            rgba(10, 10, 10, 0.4) 40%,
            transparent 100%
        );
    }

    .hero-body {
        position: relative;
        z-index: 3;
        padding: 3rem 2.5rem;
        max-width: 680px;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(229, 9, 20, 0.15);
        border: 1px solid rgba(229, 9, 20, 0.4);
        border-radius: 20px;
        padding: 0.35rem 1rem;
        font-size: 0.75rem;
        font-weight: 700;
        color: #E50914;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(8px);
    }

    .hero-heading {
        font-size: clamp(2.4rem, 5vw, 4.2rem);
        font-weight: 800;
        line-height: 1.08;
        letter-spacing: -1.5px;
        color: #FFFFFF;
        margin-bottom: 1rem;
        text-shadow: 0 4px 24px rgba(0, 0, 0, 0.8);
    }

    .hero-heading .red-accent {
        color: #E50914;
    }

    .hero-desc {
        font-size: 1.05rem;
        color: rgba(255, 255, 255, 0.75);
        line-height: 1.65;
        margin-bottom: 1.5rem;
    }

    .hero-details-meta {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-size: 0.88rem;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 1.8rem;
        flex-wrap: wrap;
    }
    .hero-details-meta .star {
        color: #FFD700;
        font-weight: 700;
    }

    /* ── Section Titles ──────────────────────────────────────────────────── */
    .section-eyebrow {
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #E50914;
        margin-bottom: 0.3rem;
    }

    .section-headline {
        font-size: 1.65rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
    }

    .section-subheadline {
        font-size: 0.88rem;
        color: #8A8A8A;
        margin-bottom: 1.5rem;
    }

    /* ── Movie Card ──────────────────────────────────────────────────────── */
    .movie-card {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex;
        flex-direction: column;
        height: 100%;
        position: relative;
        margin-bottom: 0.8rem;
    }

    .movie-card:hover {
        transform: translateY(-6px);
        border-color: rgba(229, 9, 20, 0.4);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(229, 9, 20, 0.15);
    }

    .movie-poster-wrap {
        position: relative;
        width: 100%;
        aspect-ratio: 2/3;
        background: #1c1c1c;
        overflow: hidden;
    }

    .movie-poster-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        transition: transform 0.4s ease;
    }

    .movie-card:hover .movie-poster-img {
        transform: scale(1.05);
    }

    .movie-poster-fallback {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1c1c1c 0%, #121212 100%);
        color: #555555;
        padding: 1rem;
        text-align: center;
    }
    .movie-poster-fallback .fallback-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #E50914;
        opacity: 0.7;
    }
    .movie-poster-fallback .fallback-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #888888;
        line-height: 1.3;
    }

    .badge-ai-match {
        position: absolute;
        top: 8px;
        right: 8px;
        background: linear-gradient(135deg, rgba(229, 9, 20, 0.95), rgba(184, 7, 16, 0.95));
        color: #FFFFFF;
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        z-index: 2;
    }

    .badge-rank {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(10, 10, 10, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #E50914;
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 0.72rem;
        font-weight: 800;
        z-index: 2;
    }

    .movie-meta-wrap {
        padding: 0.75rem 0.85rem;
        display: flex;
        flex-direction: column;
        flex: 1;
        justify-content: space-between;
    }

    .movie-card-name {
        font-size: 0.88rem;
        font-weight: 700;
        color: #FFFFFF;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.3rem;
    }

    .movie-card-sub {
        font-size: 0.72rem;
        color: #8A8A8A;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.4rem;
    }
    .movie-card-sub .rating-star {
        color: #FFD700;
        font-weight: 700;
    }

    .genre-tag {
        display: inline-block;
        background: rgba(229, 9, 20, 0.12);
        border: 1px solid rgba(229, 9, 20, 0.25);
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.62rem;
        font-weight: 600;
        color: #FF6B6B;
        margin-right: 3px;
        margin-bottom: 3px;
    }

    /* ── Stat Card ───────────────────────────────────────────────────────── */
    .stat-card-box {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.4rem 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card-box:hover {
        border-color: rgba(229, 9, 20, 0.3);
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .stat-card-num {
        font-size: 2rem;
        font-weight: 800;
        color: #E50914;
        letter-spacing: -1px;
        display: block;
        margin-bottom: 0.2rem;
    }
    .stat-card-tag {
        font-size: 0.72rem;
        font-weight: 700;
        color: #8A8A8A;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ── Genre Tile ──────────────────────────────────────────────────────── */
    .genre-pill {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1.1rem 0.8rem;
        text-align: center;
        transition: all 0.25s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.3rem;
    }
    .genre-pill:hover {
        background: rgba(229, 9, 20, 0.12);
        border-color: #E50914;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(229, 9, 20, 0.2);
    }
    .genre-pill-icon {
        font-size: 1.6rem;
    }
    .genre-pill-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #E0E0E0;
        letter-spacing: 0.5px;
    }

    /* ── Score Breakdown Bars ────────────────────────────────────────────── */
    .score-metric-row {
        margin-bottom: 0.75rem;
    }
    .score-metric-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        margin-bottom: 0.3rem;
    }
    .score-metric-label {
        color: #AAAAAA;
        font-weight: 500;
    }
    .score-metric-val {
        color: #FFFFFF;
        font-weight: 700;
    }
    .score-metric-track {
        height: 6px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 4px;
        overflow: hidden;
    }
    .score-metric-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* ── AI Control Panel ────────────────────────────────────────────────── */
    .ai-control-card {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .ai-control-header {
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #E50914;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 0.6rem;
        margin-bottom: 1rem;
    }

    /* ── Cold Start Banner ───────────────────────────────────────────────── */
    .cold-start-box {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 1.2rem;
        color: #FDE68A;
        font-size: 0.82rem;
        line-height: 1.5;
    }

    /* ── Movie Details Banner ────────────────────────────────────────────── */
    .details-hero {
        position: relative;
        width: 100%;
        min-height: 320px;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 2rem;
        display: flex;
        align-items: flex-end;
        background-color: #121212;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .details-hero-bg {
        position: absolute;
        inset: 0;
        background-size: cover;
        background-position: center 25%;
        z-index: 1;
    }
    .details-hero-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to top, #0a0a0a 0%, rgba(10, 10, 10, 0.8) 50%, rgba(10, 10, 10, 0.3) 100%),
                    linear-gradient(to right, #0a0a0a 0%, rgba(10, 10, 10, 0.6) 40%, transparent 100%);
        z-index: 2;
    }
    .details-hero-content {
        position: relative;
        z-index: 3;
        padding: 2rem;
        max-width: 800px;
    }

    /* ── Architecture Step Box ───────────────────────────────────────────── */
    .arch-step-box {
        background: #141414;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 600;
        color: #CCCCCC;
        margin-bottom: 0.4rem;
    }
    .arch-step-box.active-red {
        border-color: rgba(229, 9, 20, 0.4);
        background: rgba(229, 9, 20, 0.08);
        color: #FFFFFF;
    }
    .arch-step-box.active-blue {
        border-color: rgba(88, 166, 255, 0.4);
        background: rgba(88, 166, 255, 0.08);
        color: #58A6FF;
    }
    .arch-arrow-down {
        text-align: center;
        color: rgba(255, 255, 255, 0.25);
        font-size: 0.9rem;
        line-height: 1;
        margin: 0.1rem 0;
    }

    /* ── Footer ──────────────────────────────────────────────────────────── */
    .cineai-footer-box {
        margin-top: 4rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2.5rem 0 1.5rem;
        text-align: center;
    }
    .cineai-footer-brand {
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        font-weight: 900;
        letter-spacing: 1px;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }
    .cineai-footer-brand .red-accent {
        color: #E50914;
    }
    .cineai-footer-tag {
        font-size: 0.8rem;
        color: #8A8A8A;
        margin-bottom: 1rem;
    }
    .cineai-footer-notes {
        font-size: 0.68rem;
        color: #4A4A4A;
        line-height: 1.6;
    }

    /* ── Custom Scrollbar ────────────────────────────────────────────────── */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #252525;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #E50914;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
