"""
src/ui/navigation.py
--------------------
Sticky navigation bar, brand lockup, user profile, and cinematic footer for CineAI.
Pure native Streamlit session state routing.
"""

from __future__ import annotations

import streamlit as st

from src.profile import initialize_profile_state, profile


def get_cineai_logo_html(size: str = "medium") -> str:
    """
    Generate the official professional CineAI vector emblem & typography.
    """
    if size == "large":
        svg_size = 40
        font_size = "1.85rem"
        badge_font = "0.95rem"
        tag_size = "0.52rem"
    elif size == "small":
        svg_size = 24
        font_size = "1.1rem"
        badge_font = "0.62rem"
        tag_size = "0.38rem"
    else:
        svg_size = 30
        font_size = "1.3rem"
        badge_font = "0.74rem"
        tag_size = "0.42rem"

    return f"""
    <div class="cineai-pro-brand" style="display:flex;align-items:center;gap:11px;text-decoration:none;user-select:none;">
        <svg width="{svg_size}" height="{svg_size}" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 0 8px rgba(229,9,20,0.6));flex-shrink:0;">
            <defs>
                <linearGradient id="proLogoRedNav" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#FF2E3B" />
                    <stop offset="100%" stop-color="#B80710" />
                </linearGradient>
                <linearGradient id="proLogoDarkNav" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#262626" />
                    <stop offset="100%" stop-color="#0F0F0F" />
                </linearGradient>
            </defs>
            <polygon points="20,2 36,11 36,29 20,38 4,29 4,11" stroke="url(#proLogoRedNav)" stroke-width="2" fill="url(#proLogoDarkNav)"/>
            <path d="M20 6 L20 16 M32 13 L24 19 M32 27 L22 23 M20 34 L20 24 M8 27 L16 21 M8 13 L18 17" stroke="#E50914" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
            <circle cx="20" cy="20" r="4.5" fill="url(#proLogoRedNav)" />
            <circle cx="18.5" cy="18.5" r="1.5" fill="#FFFFFF" opacity="0.9" />
        </svg>
        <div style="display:flex;flex-direction:column;line-height:1;">
            <div style="display:flex;align-items:center;gap:5px;">
                <span style="font-family:'Cinzel',serif;font-size:{font_size};font-weight:900;letter-spacing:1.5px;color:#FFFFFF;background:linear-gradient(180deg,#FFFFFF 30%,#D0D0D0 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">CINE</span>
                <span style="background:linear-gradient(135deg,#E50914 0%,#B80710 100%);color:#FFFFFF;font-family:'Plus Jakarta Sans',sans-serif;font-size:{badge_font};font-weight:800;letter-spacing:1px;padding:2px 6px;border-radius:4px;box-shadow:0 0 10px rgba(229,9,20,0.5);display:inline-block;">AI</span>
            </div>
            <span style="font-size:{tag_size};font-weight:800;letter-spacing:2.5px;color:#888888;text-transform:uppercase;margin-top:3px;font-family:'Plus Jakarta Sans',sans-serif;">DISCOVER \u2022 PREDICT \u2022 WATCH</span>
        </div>
    </div>
    """


def render_navbar(active_page: str = "Home"):
    """
    Render a responsive, functional navbar at the top of the viewport.
    Navigates reliably via st.session_state['page'].
    """
    initialize_profile_state()
    if "page" not in st.session_state:
        st.session_state["page"] = active_page

    current_page = st.session_state.get("page", active_page)

    with st.container():
        st.markdown('<div class="cineai-navbar-anchor"></div>', unsafe_allow_html=True)
        nav_cols = st.columns([2.1, 0.7, 1.4, 0.8, 1.05, 1.15, 1.15, 0.85, 1.25], gap="small")

        with nav_cols[0]:
            st.markdown(get_cineai_logo_html(size="medium"), unsafe_allow_html=True)

        items = [
            ("Home", "Home"),
            ("Recommendations", "Recommendations"),
            ("Movies", "Movies"),
            ("\U0001F50D Search", "Search"),
            ("\u2764\uFE0F Favorites", "Favorites"),
            ("\U0001F4CA Analytics", "Analytics"),
            ("\u2139\uFE0F About", "About"),
        ]

        for i, (label, pkey) in enumerate(items):
            with nav_cols[i + 1]:
                is_active = (current_page == pkey)
                btn_type = "primary" if is_active else "secondary"
                if st.button(label, key=f"nav_btn_{pkey}", type=btn_type, use_container_width=True):
                    if current_page != pkey:
                        st.session_state["page"] = pkey
                        st.rerun()

        with nav_cols[8]:
            user = profile()
            name = user.get("name", "Vinit")
            with st.popover(f"{name}", use_container_width=True):
                from src.ui.profile import render_profile_menu
                render_profile_menu()


def render_footer():
    """Render the premium cinematic footer with attribution badges.

    Uses st.html() to bypass Streamlit's HTML sanitizer for complex nested HTML.
    """
    logo_html = get_cineai_logo_html(size="medium")

    st.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;500;600;700&display=swap');
        .ft {{
            margin-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.06);
            padding: 2.5rem 2rem 2rem;
            background: rgba(8,8,8,0.95);
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        .ft-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}
        .ft-brand {{
            display: flex;
            flex-direction: column;
        }}
        .ft-tagline {{
            font-size: 0.78rem;
            color: #E50914;
            font-weight: 600;
            margin-top: 0.25rem;
        }}
        .ft-badges {{
            display: flex;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        .ft-badge {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.78rem;
            color: #888;
        }}
        .ft-badge strong {{
            color: #CCC;
            font-weight: 700;
        }}
        .ft-right {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.5rem;
        }}
        .ft-cursive {{
            font-family: 'Dancing Script', cursive;
            font-size: 1.3rem;
            color: #888;
            font-style: italic;
        }}
        .ft-social {{
            display: flex;
            gap: 0.8rem;
        }}
        .ft-social-icon {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: rgba(255,255,255,0.06);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
            font-size: 0.65rem;
            font-weight: 700;
            cursor: pointer;
        }}
    </style>
    <div class="ft">
        <div class="ft-inner">
            <div class="ft-brand">
                {logo_html}
                <div class="ft-tagline">More Movies. Better Choices.</div>
            </div>
            <div class="ft-badges">
                <div class="ft-badge">
                    <span>\U0001F9E0</span>
                    <span>Powered by <strong>Machine Learning</strong></span>
                </div>
                <div class="ft-badge">
                    <span>\U0001F3AC</span>
                    <span>Built with <strong>MovieLens</strong></span>
                </div>
                <div class="ft-badge">
                    <span>\U0001F39E\uFE0F</span>
                    <span>Enhanced with <strong>TMDB</strong></span>
                </div>
            </div>
            <div class="ft-right">
                <div class="ft-cursive">Movies make a better you.</div>
                <div class="ft-social">
                    <div class="ft-social-icon">GH</div>
                    <div class="ft-social-icon">IN</div>
                    <div class="ft-social-icon">YT</div>
                </div>
            </div>
        </div>
    </div>
    """)
