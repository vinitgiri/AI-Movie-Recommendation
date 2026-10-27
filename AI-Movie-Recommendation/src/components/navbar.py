"""
src/components/navbar.py
-----------------------
Professional sticky navigation bar and cinematic brand lockup for CineAI.
"""

from __future__ import annotations

import streamlit as st


def get_cineai_logo_html(size: str = "medium") -> str:
    """
    Generate professional vector SVG and typographic lockup for CineAI.
    """
    if size == "large":
        svg_size = 38
        font_size = "1.8rem"
        badge_font = "0.95rem"
        tag_size = "0.52rem"
    else:
        svg_size = 28
        font_size = "1.25rem"
        badge_font = "0.72rem"
        tag_size = "0.42rem"

    return f"""
    <div class="cineai-pro-brand" style="display:flex;align-items:center;gap:10px;text-decoration:none;user-select:none;">
        <svg width="{svg_size}" height="{svg_size}" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 0 8px rgba(229,9,20,0.6));flex-shrink:0;">
            <defs>
                <linearGradient id="proLogoRed" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#FF334B" />
                    <stop offset="100%" stop-color="#B80710" />
                </linearGradient>
                <linearGradient id="proLogoDark" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#2A2A2A" />
                    <stop offset="100%" stop-color="#121212" />
                </linearGradient>
            </defs>
            <!-- Hexagonal Outer Shield -->
            <polygon points="20,2 36,11 36,29 20,38 4,29 4,11" stroke="url(#proLogoRed)" stroke-width="2" fill="url(#proLogoDark)"/>
            <!-- Aperture / Neural Rays -->
            <path d="M20 6 L20 16 M32 13 L24 19 M32 27 L22 23 M20 34 L20 24 M8 27 L16 21 M8 13 L18 17" stroke="#E50914" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
            <!-- Center Ruby Core -->
            <circle cx="20" cy="20" r="4.5" fill="url(#proLogoRed)" />
            <circle cx="18.5" cy="18.5" r="1.5" fill="#FFFFFF" opacity="0.9" />
        </svg>
        <div style="display:flex;flex-direction:column;line-height:1;">
            <div style="display:flex;align-items:center;gap:5px;">
                <span style="font-family:'Cinzel',serif;font-size:{font_size};font-weight:900;letter-spacing:1.5px;color:#FFFFFF;background:linear-gradient(180deg,#FFFFFF 30%,#D0D0D0 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">CINE</span>
                <span style="background:linear-gradient(135deg,#E50914 0%,#B80710 100%);color:#FFFFFF;font-family:'Plus Jakarta Sans',sans-serif;font-size:{badge_font};font-weight:800;letter-spacing:1px;padding:2px 6px;border-radius:4px;box-shadow:0 0 10px rgba(229,9,20,0.5);display:inline-block;">AI</span>
            </div>
            <span style="font-size:{tag_size};font-weight:800;letter-spacing:2.5px;color:#888888;text-transform:uppercase;margin-top:3px;font-family:'Plus Jakarta Sans',sans-serif;">STUDIO INTELLIGENCE</span>
        </div>
    </div>
    """


def render_navbar(active_page: str = "Home"):
    """
    Render a clean, responsive sticky navbar at the top of every page.
    Uses native Streamlit buttons with session state routing.
    """
    if "page" not in st.session_state:
        st.session_state["page"] = active_page

    current_page = st.session_state.get("page", active_page)

    # Outer container
    st.markdown('<div class="cineai-navbar-container">', unsafe_allow_html=True)

    nav_cols = st.columns([2.6, 0.9, 1.3, 0.9, 0.9, 1.0, 1.0, 0.8, 1.1], gap="small")

    # Col 0: Brand Logo
    with nav_cols[0]:
        st.markdown(get_cineai_logo_html(size="medium"), unsafe_allow_html=True)

    # Nav items configuration: (display_label, page_key)
    items = [
        ("Home", "Home"),
        ("Recommend", "Recommendations"),
        ("Movies", "Movies"),
        ("Search", "Search"),
        ("Favorites", "Favorites"),
        ("Analytics", "Analytics"),
        ("About", "About"),
    ]

    for i, (label, pkey) in enumerate(items):
        with nav_cols[i + 1]:
            is_active = (current_page == pkey)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_btn_{pkey}", type=btn_type, use_container_width=True):
                if current_page != pkey:
                    st.session_state["page"] = pkey
                    st.rerun()

    # Col 8: Watchlist Badge / Quick Counter
    with nav_cols[8]:
        fav_count = len(st.session_state.get("favorites", []))
        if st.button(
            f"❤️ {fav_count}" if fav_count > 0 else "🤍 0",
            key="nav_fav_counter",
            help="View Watchlist",
            use_container_width=True,
        ):
            if current_page != "Favorites":
                st.session_state["page"] = "Favorites"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """Render the cinematic footer at the bottom of the page."""
    logo_footer = get_cineai_logo_html(size="medium")
    st.markdown(f"""
    <div class="cineai-footer-box">
        <div style="display:flex;justify-content:center;margin-bottom:0.8rem;">
            {logo_footer}
        </div>
        <div class="cineai-footer-tag">
            AI-Powered Personalized Movie Recommendation Engine
        </div>
        <div class="cineai-footer-notes">
            Built with MovieLens 1M Dataset (3,883 Movies · 6,040 Users · 1M+ Ratings)<br>
            Powered by TF-IDF Vectorization • Cosine Similarity • SVD Latent Matrix Factorization • Weighted Hybrid Fusion<br>
            Posters and metadata dynamically enriched via TMDB.
        </div>
    </div>
    """, unsafe_allow_html=True)
