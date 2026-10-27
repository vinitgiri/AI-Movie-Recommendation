"""
src/ui/styles.py
----------------
High-end cinematic dark design system for CineAI.
Injects comprehensive CSS for full-width layout, typography, navigation,
hero banner, movie cards, score bars, and custom widgets.
"""

from __future__ import annotations

import streamlit as st


def inject_global_css():
    """Inject global CSS into the Streamlit session."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Cinzel:wght@700;800;900&family=Dancing+Script:wght@400;500;600;700&display=swap');

/* ── Reset & Core ──────────────────────────────────────────────────────────── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: #0A0A0A !important;
    color: #F5F5F5 !important;
}

/* Hide standard Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer, [data-testid="stToolbar"],
.stDeployButton, [data-testid="manage-app-button"] {
    display: none !important;
}

/* Hide default sidebar entirely and remove leftover offset */
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    transform: none !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main {
    margin-left: 0 !important;
    padding-left: 0 !important;
}

/* Full-width container with responsive max-width */
.main .block-container,
[data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    padding-top: 0 !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    margin: 0 auto !important;
    overflow-x: visible !important;
}

@media (min-width: 1600px) {
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }
}

/* ── Sticky Top Navbar ────────────────────────────────────────────────────── */
.cineai-navbar-anchor {
    display: none !important;
}

[data-testid="stElementContainer"]:has(.cineai-navbar-anchor),
[data-testid="element-container"]:has(.cineai-navbar-anchor) {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor),
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: rgba(10, 10, 10, 0.92);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    padding: 0.45rem 0;
    margin: 0;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.6);
    overflow: visible;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="stHorizontalBlock"],
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    flex-wrap: nowrap !important;
    gap: 0.35rem !important;
    max-width: 100%;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"],
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"] {
    min-width: 0 !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:first-child,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:first-child {
    overflow: visible !important;
}

[data-testid="stMarkdownContainer"] p:empty,
[data-testid="stMarkdownContainer"]:has(> p:empty) {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Streamlit Navigation Button Overrides ────────────────────────────────── */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) .stButton > button,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) .stButton > button {
    height: 36px !important;
    padding: 0 0.7rem !important;
    font-size: 0.78rem !important;
    white-space: nowrap !important;
    font-weight: 600 !important;
    border-radius: 20px !important;
    letter-spacing: 0.3px !important;
    background: transparent !important;
    border: none !important;
    color: #A3A3A3 !important;
    transition: all 0.25s ease !important;
    box-shadow: none !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) .stButton > button:hover,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) .stButton > button:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #FFFFFF !important;
    transform: none !important;
    box-shadow: none !important;
    border: none !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) .stButton > button[kind="primary"],
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #E50914 0%, #B80710 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 12px rgba(229, 9, 20, 0.4) !important;
    border-radius: 20px !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) .stButton > button[kind="primary"]:hover,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #FF1F2D 0%, #D40813 100%) !important;
    box-shadow: 0 4px 18px rgba(229, 9, 20, 0.5) !important;
    transform: none !important;
}

/* ── Standard Streamlit Buttons ───────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
    padding: 0.45rem 1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: #141414 !important;
    color: #E0E0E0 !important;
}

.stButton > button:hover {
    background: #202020 !important;
    border-color: rgba(229, 9, 20, 0.5) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(229, 9, 20, 0.2);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #E50914 0%, #B80710 100%) !important;
    border: 1px solid #E50914 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 18px rgba(229, 9, 20, 0.4) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #FF1F2D 0%, #D40813 100%) !important;
    box-shadow: 0 6px 24px rgba(229, 9, 20, 0.6) !important;
    transform: translateY(-2px);
}

/* ── Full Cinematic Hero ──────────────────────────────────────────────────── */
.hero-container {
    position: relative;
    width: calc(100% + 3rem);
    margin-left: -1.5rem;
    height: clamp(360px, 39vw, 630px);
    min-height: 0;
    aspect-ratio: 16 / 7;
    overflow: hidden;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    background-color: #0E0E0E;
}

@media (min-width: 1600px) {
    .hero-container {
        width: calc(100% + 6rem);
        margin-left: -3rem;
    }
}

.hero-bg-art {
    position: absolute;
    inset: 0;
    z-index: 1;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

.hero-overlay-radial {
    position: absolute;
    inset: 0;
    z-index: 2;
    background:
        linear-gradient(
            to right,
            rgba(10, 10, 10, 0.97) 0%,
            rgba(10, 10, 10, 0.90) 30%,
            rgba(10, 10, 10, 0.55) 60%,
            rgba(10, 10, 10, 0.20) 80%,
            rgba(10, 10, 10, 0.10) 100%
        ),
        linear-gradient(
            to top,
            rgba(10, 10, 10, 1) 0%,
            rgba(10, 10, 10, 0.6) 25%,
            transparent 100%
        );
}

.hero-left-content {
    position: relative;
    z-index: 3;
    padding: 3.5rem 3rem;
    max-width: 620px;
}

.hero-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(229, 9, 20, 0.12);
    border: 1px solid rgba(229, 9, 20, 0.4);
    border-radius: 20px;
    padding: 0.35rem 0.95rem;
    font-size: 0.68rem;
    font-weight: 800;
    color: #E50914;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(8px);
}

.hero-main-title {
    font-size: clamp(2.6rem, 5vw, 4.2rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -1.5px;
    color: #FFFFFF;
    margin-bottom: 1rem;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.9);
}

.hero-main-title .red-text {
    color: #E50914;
    text-shadow: 0 0 30px rgba(229, 9, 20, 0.4);
}

.hero-synopsis {
    font-size: 0.95rem;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.6;
    margin-bottom: 1.5rem;
    font-weight: 400;
    max-width: 500px;
}

.hero-metadata-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 0.88rem;
    color: rgba(255, 255, 255, 0.65);
    margin-bottom: 0;
    flex-wrap: wrap;
}

.hero-metadata-row .gold-star {
    color: #FFD700;
    font-weight: 700;
}

/* Hero CTA Buttons Row */
.hero-cta-row {
    display: flex;
    gap: 1rem;
    margin-top: 1.8rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.hero-btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, #E50914 0%, #B80710 100%);
    color: #FFFFFF;
    font-size: 0.88rem;
    font-weight: 700;
    padding: 0.7rem 1.6rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 4px 18px rgba(229, 9, 20, 0.4);
    text-decoration: none;
    letter-spacing: 0.3px;
}

.hero-btn-primary:hover {
    background: linear-gradient(135deg, #FF1F2D 0%, #D40813 100%);
    box-shadow: 0 6px 24px rgba(229, 9, 20, 0.6);
    transform: translateY(-2px);
}

.hero-btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: transparent;
    color: #FFFFFF;
    font-size: 0.88rem;
    font-weight: 600;
    padding: 0.7rem 1.6rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    cursor: pointer;
    transition: all 0.25s ease;
    text-decoration: none;
    letter-spacing: 0.3px;
}

.hero-btn-secondary:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
}

/* Hero Right Side Info Card */
.hero-right-preview {
    position: absolute;
    bottom: 2.5rem;
    right: 3rem;
    z-index: 3;
    background: rgba(14, 14, 14, 0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    max-width: 340px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.7);
}

.hero-preview-label {
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 1.8px;
    color: #E50914;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.hero-preview-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.4rem;
    line-height: 1.25;
}

.hero-preview-meta {
    font-size: 0.78rem;
    color: #888888;
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.6rem;
    align-items: center;
}

.hero-preview-desc {
    font-size: 0.78rem;
    color: #AAAAAA;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.hero-nav-arrows {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.8rem;
    justify-content: flex-end;
}

.hero-nav-arrows .hero-arrow-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.hero-nav-arrows .hero-arrow-btn:hover {
    background: rgba(229, 9, 20, 0.3);
    border-color: rgba(229, 9, 20, 0.6);
}

/* ── Stats Strip ──────────────────────────────────────────────────────────── */
.stats-strip {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 2.5rem;
    padding: 1.5rem 0;
    flex-wrap: wrap;
}

.stat-inline-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.stat-inline-icon {
    font-size: 1.1rem;
    color: #E50914;
    opacity: 0.8;
}

.stat-inline-number {
    font-size: 1.5rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.5px;
    line-height: 1;
}

.stat-inline-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8A8A8A;
    text-transform: capitalize;
}

.stat-inline-text {
    display: flex;
    flex-direction: column;
}

/* ── Section Titles ──────────────────────────────────────────────────────── */
.section-eyebrow {
    font-size: 0.7rem;
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
    margin-bottom: 1.3rem;
}

/* Section Header Row */
.section-header-row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 1.2rem;
    margin-top: 2rem;
}

.section-header-left {
    display: flex;
    flex-direction: column;
}

.section-view-all {
    font-size: 0.82rem;
    font-weight: 600;
    color: #E50914;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.section-view-all:hover {
    color: #FF3333;
    text-decoration: underline;
}

/* ── Movie Card ──────────────────────────────────────────────────────────── */
.movie-card-box {
    background: #141414;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.3s ease, border-color 0.3s ease;
    margin-bottom: 0.6rem;
}

.movie-card-box:hover {
    transform: translateY(-6px);
    border-color: rgba(229, 9, 20, 0.45);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(229, 9, 20, 0.15);
}

.movie-poster-frame {
    position: relative;
    width: 100%;
    aspect-ratio: 2/3;
    background: #1a1a1a;
    overflow: hidden;
}

.movie-poster-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.4s ease;
}

.movie-card-box:hover .movie-poster-img {
    transform: scale(1.05);
}

/* Pro Local Placeholder */
.movie-poster-pro-fallback {
    width: 100%;
    height: 100%;
    background: linear-gradient(145deg, #1f1f1f 0%, #121212 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    text-align: center;
}

.movie-poster-pro-fallback svg {
    filter: drop-shadow(0 0 6px rgba(229,9,20,0.4));
    margin-bottom: 0.6rem;
}

.movie-poster-pro-fallback .fb-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #999999;
    line-height: 1.3;
}

.badge-ai-pill {
    position: absolute;
    top: 8px;
    right: 8px;
    background: linear-gradient(135deg, rgba(229, 9, 20, 0.95), rgba(184, 7, 16, 0.95));
    color: #FFFFFF;
    border-radius: 6px;
    padding: 3px 7px;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    z-index: 2;
}

.badge-rank-pill {
    position: absolute;
    top: 8px;
    left: 8px;
    background: rgba(10, 10, 10, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #E50914;
    border-radius: 6px;
    padding: 2px 7px;
    font-size: 0.72rem;
    font-weight: 800;
    z-index: 2;
}

.movie-card-info-wrap {
    padding: 0.75rem 0.85rem;
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: space-between;
}

.movie-card-main-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #FFFFFF;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.3rem;
}

.movie-card-sub-meta {
    font-size: 0.72rem;
    color: #8A8A8A;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}

.genre-tag-pill {
    display: inline-block;
    background: rgba(229, 9, 20, 0.1);
    border: 1px solid rgba(229, 9, 20, 0.25);
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 0.62rem;
    font-weight: 600;
    color: #FF6B6B;
    margin-right: 3px;
    margin-bottom: 2px;
}

/* ── Trending Card (compact poster card) ──────────────────────────────────── */
.trending-card {
    background: #141414;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    margin-bottom: 0.5rem;
}

.trending-card:hover {
    transform: translateY(-6px);
    border-color: rgba(229, 9, 20, 0.4);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.7), 0 0 15px rgba(229, 9, 20, 0.12);
}

.trending-poster-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 2/3;
    overflow: hidden;
    background: #1a1a1a;
}

.trending-poster-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.4s ease;
}

.trending-card:hover .trending-poster-wrap img {
    transform: scale(1.06);
}

.trending-info {
    padding: 0.65rem 0.75rem;
}

.trending-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #FFFFFF;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.25rem;
}

.trending-meta {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.72rem;
    color: #8A8A8A;
}

.trending-meta .t-star {
    color: #FFD700;
    font-weight: 700;
}

/* ── Stat Card ───────────────────────────────────────────────────────────── */
.stat-card-box {
    background: #141414;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.4rem 1rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card-box:hover {
    border-color: rgba(229, 9, 20, 0.4);
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
    text-shadow: 0 0 20px rgba(229, 9, 20, 0.3);
}

.stat-card-tag {
    font-size: 0.72rem;
    font-weight: 700;
    color: #8A8A8A;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Genre Card ──────────────────────────────────────────────────────────── */
.genre-visual-card {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    padding: 1.2rem 0.8rem;
    background: linear-gradient(135deg, #181818 0%, #111111 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    transition: all 0.25s ease;
    margin-bottom: 0.5rem;
    cursor: pointer;
}

.genre-visual-card:hover {
    border-color: rgba(229, 9, 20, 0.5);
    background: rgba(229, 9, 20, 0.06);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(229, 9, 20, 0.15);
}

.genre-icon-circle {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.6rem;
    font-size: 1.5rem;
    transition: all 0.25s ease;
}

.genre-visual-card:hover .genre-icon-circle {
    background: rgba(229, 9, 20, 0.12);
    border-color: rgba(229, 9, 20, 0.35);
}

.genre-visual-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.5px;
}

/* ── Premium Footer ──────────────────────────────────────────────────────── */
.cineai-footer {
    margin-top: 4rem;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: 2.5rem 0 2rem;
    width: calc(100% + 3rem);
    margin-left: -1.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
    background: rgba(8, 8, 8, 0.95);
}

@media (min-width: 1600px) {
    .cineai-footer {
        width: calc(100% + 6rem);
        margin-left: -3rem;
        padding-left: 3.5rem;
        padding-right: 3.5rem;
    }
}

.footer-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.footer-brand {
    display: flex;
    flex-direction: column;
}

.footer-tagline {
    font-size: 0.78rem;
    color: #E50914;
    font-weight: 600;
    margin-top: 0.25rem;
    letter-spacing: 0.2px;
}

.footer-badges {
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
}

.footer-badge-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    color: #888888;
}

.footer-badge-icon {
    font-size: 1rem;
    color: #666666;
}

.footer-badge-item strong {
    color: #CCCCCC;
    font-weight: 700;
}

.footer-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
}

.footer-cursive {
    font-family: 'Dancing Script', cursive;
    font-size: 1.3rem;
    color: #888888;
    font-style: italic;
}

.footer-social {
    display: flex;
    gap: 0.8rem;
}

.footer-social-icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888888;
    font-size: 0.8rem;
    transition: all 0.2s ease;
    cursor: pointer;
}

.footer-social-icon:hover {
    background: rgba(229, 9, 20, 0.2);
    color: #FFFFFF;
}

/* ── AI Control Panel ────────────────────────────────────────────────────── */
.ai-control-card {
    background: #141414;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.4rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.ai-control-header {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #E50914;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 0.6rem;
    margin-bottom: 1.2rem;
}

/* ── Recommendations Responsive Grid ─────────────────────────────────────── */
.rec-grid-anchor { display: none !important; }

[data-testid="column"]:has(.rec-grid-anchor) [data-testid="stHorizontalBlock"]:has(> [data-testid="column"] .movie-card-box) {
    flex-wrap: wrap !important;
    row-gap: 1rem !important;
}

/* Laptop: 3 cards per row */
@media (max-width: 1100px) {
    [data-testid="column"]:has(.rec-grid-anchor) [data-testid="stHorizontalBlock"]:has(> [data-testid="column"] .movie-card-box) > [data-testid="column"] {
        flex: 1 1 calc(33.333% - 0.7rem) !important;
        min-width: calc(33.333% - 0.7rem) !important;
        max-width: calc(33.333% - 0.7rem) !important;
    }
}

/* Tablet: 2 cards per row */
@media (max-width: 700px) {
    [data-testid="column"]:has(.rec-grid-anchor) [data-testid="stHorizontalBlock"]:has(> [data-testid="column"] .movie-card-box) > [data-testid="column"] {
        flex: 1 1 calc(50% - 0.5rem) !important;
        min-width: calc(50% - 0.5rem) !important;
        max-width: calc(50% - 0.5rem) !important;
    }
}

/* Phone: 1 card per row */
@media (max-width: 420px) {
    [data-testid="column"]:has(.rec-grid-anchor) [data-testid="stHorizontalBlock"]:has(> [data-testid="column"] .movie-card-box) > [data-testid="column"] {
        flex: 1 1 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
    }
}

/* ── Cold Start Banner ───────────────────────────────────────────────────── */
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

/* ── Movie Details Banner ────────────────────────────────────────────────── */
.details-hero {
    position: relative;
    width: 100%;
    min-height: 340px;
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
    background: linear-gradient(to top, #0A0A0A 0%, rgba(10, 10, 10, 0.85) 55%, rgba(10, 10, 10, 0.3) 100%),
                linear-gradient(to right, #0A0A0A 0%, rgba(10, 10, 10, 0.6) 40%, transparent 100%);
    z-index: 2;
}

.details-hero-content {
    position: relative;
    z-index: 3;
    padding: 2.2rem;
    max-width: 850px;
}

/* ── Score Breakdown Bars ────────────────────────────────────────────────── */
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

/* ── Streamlit Inputs ────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
    background: #141414 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-size: 0.92rem !important;
    padding: 0.65rem 1rem !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #E50914 !important;
    box-shadow: 0 0 0 1px #E50914 !important;
}

[data-testid="stSelectbox"] > div > div {
    background: #141414 !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}

/* User profile pill */
.user-profile-pill {
    display: flex;
    align-items: center;
    width: fit-content;
    max-width: 100%;
    white-space: nowrap;
    gap: 0.5rem;
    padding: 0.3rem 0.6rem 0.3rem 0.3rem;
    border-radius: 24px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}

.user-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, #E50914, #B80710);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 0.75rem;
}

.user-info {
    display: flex;
    flex-direction: column;
    line-height: 1.15;
}

.user-name {
    font-size: 0.78rem;
    font-weight: 700;
    color: #FFFFFF;
}

.user-role {
    font-size: 0.6rem;
    color: #888888;
    font-weight: 500;
}

.profile-avatar-large {
    width: 112px;
    height: 112px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #E50914, #B80710);
    color: #FFFFFF;
    font-size: 2.5rem;
    font-weight: 800;
    box-shadow: 0 10px 30px rgba(229, 9, 20, 0.3);
}

.profile-popover-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.8rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    color: #FFFFFF;
}

/* The actual Streamlit button (Premium chip style) */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9),
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) {
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

[data-testid="stPopover"] {
    display: flex;
    justify-content: flex-end;
    margin: 0 !important;
    padding: 0 !important;
    width: 100%;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button {
    background: rgba(18, 18, 18, 0.85) !important;
    border: 1px solid rgba(229, 9, 20, 0.35) !important;
    border-radius: 24px !important;
    height: 48px !important;
    padding: 0 16px !important;
    color: #FFFFFF !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    max-width: 220px !important;
    box-shadow: 0 4px 15px rgba(229, 9, 20, 0.15) !important;
    transition: all 0.3s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-left: auto !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button p,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    margin: 0 !important;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button::after,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button::after {
    content: "\25BC";
    font-size: 0.65rem;
    color: #888888;
    margin-left: 8px;
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button::before,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button::before {
    content: "";
    display: block;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #E50914 0%, #B80710 100%);
    margin-right: 10px;
    box-shadow: 0 0 10px rgba(229, 9, 20, 0.4);
}

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button:hover,
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .cineai-navbar-anchor) [data-testid="column"]:nth-child(9) [data-testid="stPopover"] > button:hover {
    background: rgba(26, 26, 26, 0.95) !important;
    border-color: rgba(229, 9, 20, 0.6) !important;
    box-shadow: 0 6px 20px rgba(229, 9, 20, 0.25) !important;
    transform: scale(1.02) !important;
}

[data-testid="stPopover"] [data-testid="stPopoverBody"] {
    width: min(460px, calc(100vw - 24px)) !important;
    max-height: min(680px, calc(100vh - 80px)) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    border-radius: 18px !important;
    background: rgba(12,12,12,0.98) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    box-shadow: 0 18px 55px rgba(0,0,0,0.75), 0 0 24px rgba(229,9,20,0.12) !important;
}

.profile-menu-divider {
    height: 1px;
    margin: 0.65rem 0;
    background: rgba(255,255,255,0.08);
}

.profile-section-title {
    color: #FFFFFF;
    font-size: 1rem;
    font-weight: 800;
    margin: 0.75rem 0 0.9rem;
}

.profile-popover-header span {
    color: #888888;
    font-size: 0.72rem;
}

.profile-avatar-small {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #E50914, #B80710);
    color: #FFFFFF;
    font-weight: 800;
}

.profile-avatar-small img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .hero-container {
        height: clamp(420px, 125vw, 600px);
        aspect-ratio: 4 / 5;
    }
    .hero-left-content {
        padding: 2rem 1.5rem;
        max-width: 100%;
    }
    .hero-right-preview {
        display: none;
    }
    .stats-strip {
        gap: 1.5rem;
    }
    .footer-inner {
        flex-direction: column;
        align-items: flex-start;
    }
    .footer-right {
        align-items: flex-start;
    }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0A0A0A;
}
::-webkit-scrollbar-thumb {
    background: #222222;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #E50914;
}
</style>
"""
