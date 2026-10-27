"""CineAI User Profile and Settings Center."""

from __future__ import annotations

import json
import base64
from datetime import datetime

import streamlit as st

from src.profile import (
    ERAS,
    GENRES,
    LANGUAGES,
    DEFAULT_PREFERENCES,
    initialize_profile_state,
    preferences,
    profile,
    profile_completion,
    reset_personalization,
    reset_preferences,
    save_profile,
    update_preferences,
)


def _card(title: str, body: str, accent: str = "#E50914") -> None:
    st.html(f"""
    <div style="background:#141414;border:1px solid {accent}55;border-radius:12px;padding:1.2rem;height:100%;">
        <div style="font-size:0.7rem;font-weight:800;letter-spacing:1.6px;color:{accent};margin-bottom:0.45rem;">{title}</div>
        <div style="font-size:0.88rem;color:#B8B8B8;line-height:1.55;">{body}</div>
    </div>
    """)


def _stats(ratings, favorites: list[str], recommendation_history: list) -> dict[str, str]:
    user_id = int(st.session_state.get("selected_user_id", 1))
    user_ratings = ratings[ratings["userId"] == user_id] if ratings is not None else None
    if user_ratings is None or user_ratings.empty:
        rated = "Not available"
        average = "Not available"
    else:
        rated = f"{len(user_ratings):,}"
        average = f"{user_ratings['rating'].mean():.2f} / 5"
    return {
        "Movies Rated": rated,
        "Favorites": f"{len(favorites):,}",
        "Average Rating": average,
        "Top Genre": ", ".join(profile().get("favorite_genres", [])) or "Not available",
        "Top Language": ", ".join(profile().get("preferred_languages", [])) or "Not available",
        "Recommendations": f"{len(recommendation_history):,}",
        "Movies Watched": f"{len(st.session_state.get('recently_viewed', [])):,}",
        "Searches": f"{len(st.session_state.get('search_history', [])):,}",
    }


def _render_overview(ratings) -> None:
    p = profile()
    stats = _stats(ratings, st.session_state.get("favorites", []), st.session_state.get("recommendation_history", []))
    left, right = st.columns([1.1, 2.9], gap="large")
    with left:
        if p.get("avatar_bytes"):
            st.image(p["avatar_bytes"], width=112)
        else:
            st.markdown(f"<div class=\"profile-avatar-large\">{str(p.get('name', 'V'))[:1].upper()}</div>", unsafe_allow_html=True)
    with right:
        st.markdown(f"<h2 style='margin:0;color:#FFF;'>{p.get('name', 'Vinit')}</h2>", unsafe_allow_html=True)
        st.caption(f"@{p.get('username', 'vinit')} · Movie Enthusiast · Member since {p.get('member_since', '2026')}")
        st.write(p.get("bio", ""))
        st.progress(profile_completion() / 100, text=f"Profile completion: {profile_completion()}%")

    cols = st.columns(4)
    for col, (label, value) in zip(cols, list(stats.items())[:4]):
        with col:
            _card(label, value)
    cols = st.columns(4)
    for col, (label, value) in zip(cols, list(stats.items())[4:]):
        with col:
            _card(label, value, "#58A6FF")

    st.markdown("### Current Taste Profile")
    _card(
        "PREFERENCES",
        f"Genres: {', '.join(p.get('favorite_genres', [])) or 'Not set'}<br>Languages: {', '.join(p.get('preferred_languages', [])) or 'Not set'}<br>Era: {p.get('preferred_era', 'Any')}",
        "#3FB950",
    )


def _render_edit_profile() -> None:
    p = profile()
    with st.form("profile_form"):
        name = st.text_input("Name", value=p.get("name", ""))
        username = st.text_input("Username", value=p.get("username", ""))
        bio = st.text_area("Short bio", value=p.get("bio", ""), max_chars=240)
        avatar = st.file_uploader("Avatar / profile image", type=["png", "jpg", "jpeg", "webp"])
        genres = st.multiselect("Favorite genres", GENRES, default=p.get("favorite_genres", []))
        languages = st.multiselect("Preferred languages", LANGUAGES, default=p.get("preferred_languages", []))
        era = st.selectbox("Preferred movie era", ERAS, index=ERAS.index(p.get("preferred_era", "Any")))
        save, cancel = st.columns(2)
        with save:
            submitted = st.form_submit_button("Save Profile", type="primary")
        with cancel:
            cancelled = st.form_submit_button("Cancel")
    if submitted:
        if not name.strip() or not username.strip():
            st.error("Name and username cannot be empty.")
        else:
            save_profile({"name": name.strip(), "username": username.strip(), "bio": bio.strip(), "favorite_genres": genres, "preferred_languages": languages, "preferred_era": era, "avatar_bytes": avatar.getvalue() if avatar else p.get("avatar_bytes")})
            st.success("Profile saved for this session.")
            st.rerun()
    if cancelled:
        st.info("Unsaved profile changes were discarded.")


def _render_movie_preferences() -> None:
    prefs = preferences()
    include = st.multiselect("Include genres", GENRES, default=prefs.get("include_genres", []), key="pref_include_genres")
    exclude = st.multiselect("Exclude genres", GENRES, default=prefs.get("exclude_genres", []), key="pref_exclude_genres")
    languages = st.multiselect("Preferred languages", LANGUAGES, default=profile().get("preferred_languages", []), key="pref_languages")
    era = st.selectbox("Movie era", ERAS, index=ERAS.index(profile().get("preferred_era", "Any")), key="pref_era")
    left, right = st.columns(2)
    with left:
        from_year = st.number_input("Release year from", 1900, 2026, int(prefs.get("from_year", 2006)), key="pref_from_year")
    with right:
        to_year = st.number_input("Release year to", 1900, 2026, int(prefs.get("to_year", 2026)), key="pref_to_year")
    if st.button("Save Movie Preferences", type="primary"):
        if from_year > to_year:
            st.error("The starting year must not exceed the ending year.")
        else:
            update_preferences({"include_genres": include, "exclude_genres": exclude, "from_year": from_year, "to_year": to_year})
            save_profile({"preferred_languages": languages, "preferred_era": era})
            st.success("Movie preferences saved.")


def _render_recommendation_settings() -> None:
    prefs = preferences()
    alpha = st.slider("Content Weight (α)", 0.0, 1.0, float(prefs.get("alpha", 0.5)), 0.05, key="profile_alpha")
    st.caption(f"Content: {alpha:.0%} · Collaborative: {(1 - alpha):.0%}")
    count = st.select_slider("Recommendation count", options=[5, 10, 15, 20, 30], value=int(prefs.get("recommendation_count", 10)), key="profile_count")
    minimum_rating = st.slider("Minimum rating", 0.0, 5.0, float(prefs.get("minimum_rating", 0.0)), 0.1, key="profile_min_rating")
    minimum_votes = st.slider("Minimum vote count", 0, 1000, int(prefs.get("minimum_vote_count", 0)), 10, key="profile_min_votes", disabled=True)
    popularity = st.slider("Popularity influence", 0.0, 1.0, float(prefs.get("popularity_influence", 0.0)), 0.05, key="profile_popularity", disabled=True)
    similarity = st.slider("Similarity threshold", 0.0, 1.0, float(prefs.get("similarity_threshold", 0.0)), 0.05, key="profile_similarity")
    diversity = st.selectbox("Diversity level", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(prefs.get("diversity", "Medium")))
    mode = st.selectbox("Recommendation mode", ["Hybrid Fusion", "Content Similarity", "Collaborative Filtering"], index=["Hybrid Fusion", "Content Similarity", "Collaborative Filtering"].index(prefs.get("mode", "Hybrid Fusion")))
    if st.button("Save Recommendation Settings", type="primary"):
        update_preferences({"alpha": alpha, "recommendation_count": count, "minimum_rating": minimum_rating, "minimum_vote_count": minimum_votes, "popularity_influence": popularity, "similarity_threshold": similarity, "diversity": diversity, "mode": mode})
        st.session_state["alpha_weight"] = alpha
        st.success("Recommendation settings saved and connected to the Recommendations page.")
    st.caption("Minimum vote count and popularity influence require TMDB ranking fields in the recommendation result and are currently unavailable.")


def _render_personalization() -> None:
    prefs = preferences()
    labels = [
        ("use_rating_history", "Use rating history"), ("use_favorites", "Use favorite movies"),
        ("use_search_history", "Use search history"), ("use_recently_viewed", "Use recently viewed movies"),
        ("use_liked_genres", "Use liked genres"), ("use_disliked_genres", "Use disliked genres"),
        ("use_interaction_history", "Use interaction history"),
    ]
    values = {key: st.checkbox(label, value=bool(prefs.get(key, True)), key=f"personal_{key}") for key, label in labels}
    if st.button("Save Personalization"):
        update_preferences(values)
        st.success("Personalization preferences saved.")
    if st.button("Reset Personalization"):
        reset_personalization()
        st.success("Personalization preferences reset.")
        st.rerun()


def _render_appearance() -> None:
    prefs = preferences()
    values = {
        "theme": st.selectbox("Theme", ["Dark", "Light", "System"], index=["Dark", "Light", "System"].index(prefs.get("theme", "Dark"))),
        "card_density": st.selectbox("Movie card density", ["Compact", "Comfortable", "Large"], index=["Compact", "Comfortable", "Large"].index(prefs.get("card_density", "Comfortable"))),
        "poster_size": st.selectbox("Poster size", ["Small", "Medium", "Large"], index=["Small", "Medium", "Large"].index(prefs.get("poster_size", "Medium"))),
        "grid_columns": st.selectbox("Grid columns", ["Auto", "3", "4", "5", "6"], index=["Auto", "3", "4", "5", "6"].index(prefs.get("grid_columns", "Auto"))),
        "display_language": st.selectbox("Language", ["English", "Hindi"], index=["English", "Hindi"].index(prefs.get("display_language", "English"))),
    }
    for key, label in [("show_ratings", "Ratings"), ("show_genres", "Genres"), ("show_release_year", "Release year"), ("show_overview", "Overview"), ("show_popularity", "Popularity"), ("show_recommendation_score", "Recommendation score")]:
        values[key] = st.checkbox(f"Show {label.lower()}", value=bool(prefs.get(key, True)), key=f"display_{key}")
    if st.button("Save Appearance Settings", type="primary"):
        update_preferences(values)
        st.success("Display preferences saved for this session.")


def _render_notifications() -> None:
    st.info("Notifications and authentication are not implemented in this local Streamlit app.")
    for label in ["New recommendation notifications", "Favorite movie updates", "New movie alerts", "Personalized movie suggestions", "Weekly recommendation summary"]:
        st.checkbox(label, disabled=True)
    st.selectbox("Notification frequency", ["Real-time", "Daily", "Weekly", "Off"], disabled=True)
    st.caption("Coming Soon")


def _render_privacy() -> None:
    prefs = preferences()
    for key, label in [("save_recommendation_history", "Save recommendation history"), ("save_search_history", "Save search history"), ("save_viewed_movies", "Save viewed movies"), ("save_rating_history", "Save rating history"), ("allow_activity_personalization", "Allow personalization from activity")]:
        prefs[key] = st.checkbox(label, value=bool(prefs.get(key, True)), key=f"privacy_{key}")
    st.caption("These actions only affect session history; MovieLens and application data are never deleted.")
    for key, label in [("search_history", "Clear Search History"), ("recommendation_history", "Clear Recommendation History"), ("recently_viewed", "Clear Viewing History")]:
        confirm = st.checkbox(f"Confirm {label.lower()}", key=f"confirm_{key}")
        if st.button(label, disabled=not confirm, key=f"clear_{key}"):
            st.session_state[key] = []
            st.success(f"{label} completed.")


def _render_data_management() -> None:
    p = profile()
    prefs = preferences()
    export = {"profile": {k: v for k, v in p.items() if k != "avatar_bytes"}, "preferences": prefs, "favorites": st.session_state.get("favorites", []), "recently_viewed": st.session_state.get("recently_viewed", [])}
    payload = json.dumps(export, indent=2, ensure_ascii=True)
    st.download_button("Export My Data", payload, "cineai-profile.json", "application/json")
    uploaded = st.file_uploader("Import My Data", type=["json"], key="profile_import")
    if uploaded and st.button("Apply Imported Profile"):
        data = json.loads(uploaded.getvalue().decode("utf-8"))
        if isinstance(data.get("profile"), dict) and data["profile"].get("name") and data["profile"].get("username"):
            save_profile({k: v for k, v in data["profile"].items() if k in p and k != "avatar_bytes"})
            update_preferences({k: v for k, v in data.get("preferences", {}).items() if k in prefs})
            st.success("Profile data imported.")
            st.rerun()
    st.write(f"Profile data size: {len(payload.encode('utf-8')):,} bytes")
    st.write(f"Ratings: Not available for export · Favorites: {len(st.session_state.get('favorites', []))} · Searches: {len(st.session_state.get('search_history', []))} · Recommendations: {len(st.session_state.get('recommendation_history', []))}")
    st.caption(f"Last profile update: {p.get('updated_at') or 'Not available'}")
    if st.button("Clear Personal Data", type="secondary"):
        st.session_state["favorites"] = []
        st.session_state["recently_viewed"] = []
        st.session_state["search_history"] = []
        st.session_state["recommendation_history"] = []
        st.success("Session personal data cleared. MovieLens and application data were preserved.")
    with st.expander("Account Settings"):
        st.caption("Profile editing, username changes, and avatar changes are available in the Edit Profile tab.")
        if st.button("Reset Recommendation Settings", key="account_reset_recommendation"):
            reset_preferences()
            st.success("Recommendation and display preferences reset.")
        st.button("Sign Out", disabled=True, help="Authentication is not implemented in this local app.")
        st.caption("Sign Out: Coming Soon")


def _render_advanced_ai() -> None:
    prefs = preferences()
    st.selectbox("Recommendation algorithm", ["Hybrid", "Content-Based", "Collaborative"], index=0, disabled=True)
    st.selectbox("Content similarity method", ["TF-IDF + Cosine Similarity"], disabled=True)
    st.selectbox("Collaborative method", ["SVD"], index=0, disabled=True)
    st.selectbox("Hybrid weighting", ["Manual", "Balanced", "Content-focused", "Collaborative-focused"], index=0, disabled=True)
    st.selectbox("Cold-start strategy", ["Content fallback"], disabled=True)
    st.selectbox("Diversity", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(prefs.get("diversity", "Medium")))
    prefs["explain_recommendations"] = st.checkbox("Show why this movie was recommended", value=bool(prefs.get("explain_recommendations", True)))
    st.caption("Unavailable backend options are intentionally read-only rather than simulated.")


def render_profile_menu() -> None:
    """Render the compact account menu and one selected settings section."""
    initialize_profile_state()
    from src.components.model_loader import load_models

    _, ratings, _, _, _, missing = load_models()
    if missing:
        st.error("Profile statistics are unavailable until the recommendation models are trained.")
        return

    user = profile()
    avatar_markup = f"{str(user.get('name', 'V'))[:1].upper()}"
    if user.get("avatar_bytes"):
        encoded_avatar = base64.b64encode(user["avatar_bytes"]).decode("ascii")
        avatar_markup = f"<img src='data:image/png;base64,{encoded_avatar}' alt='Profile avatar'>"
    st.markdown(
        f"<div class='profile-popover-header'><div class='profile-avatar-small'>{avatar_markup}</div><div><strong>{user.get('name', 'Vinit')}</strong><br><span>@{user.get('username', 'vinit')} · Movie Enthusiast</span></div></div>",
        unsafe_allow_html=True,
    )
    stats = _stats(ratings, st.session_state.get("favorites", []), st.session_state.get("recommendation_history", []))
    
    st.markdown(f"""
    <div style="font-size:0.75rem; color:#888888; margin-top:-0.4rem; padding-bottom:0.8rem;">
        Member since {user.get('member_since', '2026')} · {profile_completion()}% complete
    </div>
    <div class="profile-menu-divider" style="margin: 0 0 0.8rem 0;"></div>
    <div style="display:flex; justify-content:space-between; gap:0.4rem; text-align:center; padding-bottom: 0.8rem;">
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); padding:0.6rem 0.2rem; border-radius:10px;">
            <div style="font-size:1.1rem; font-weight:800; color:#FFF; line-height:1;">{stats['Movies Rated']}</div>
            <div style="font-size:0.65rem; color:#888; font-weight:600; margin-top:2px;">Rated</div>
        </div>
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); padding:0.6rem 0.2rem; border-radius:10px;">
            <div style="font-size:1.1rem; font-weight:800; color:#FFF; line-height:1;">{stats['Favorites']}</div>
            <div style="font-size:0.65rem; color:#888; font-weight:600; margin-top:2px;">Fav</div>
        </div>
        <div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); padding:0.6rem 0.2rem; border-radius:10px;">
            <div style="font-size:1.1rem; font-weight:800; color:#FFF; line-height:1;">{stats['Average Rating'].split(' ')[0]}</div>
            <div style="font-size:0.65rem; color:#888; font-weight:600; margin-top:2px;">Avg Rating</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sections = {
        "My Profile": ("👤", _render_edit_profile),
        "Movie Preferences": ("🎬", _render_movie_preferences),
        "Recommendation Settings": ("🤖", _render_recommendation_settings),
        "Personalization": ("🧠", _render_personalization),
        "Appearance": ("🎨", _render_appearance),
        "Notifications": ("🔔", _render_notifications),
        "Privacy": ("🔒", _render_privacy),
        "Data Management": ("💾", _render_data_management),
        "Advanced AI": ("⚙️", _render_advanced_ai),
    }
    selected = st.session_state.get("profile_menu_section")
    if selected not in sections:
        st.markdown("<div class='profile-menu-divider'></div>", unsafe_allow_html=True)
        for label, (icon, _) in sections.items():
            if st.button(f"{icon}  {label}", key=f"profile_menu_{label}", use_container_width=True):
                st.session_state["profile_menu_section"] = label
                st.rerun()
        st.markdown("<div class='profile-menu-divider'></div>", unsafe_allow_html=True)
        st.button("🚪  Sign Out", disabled=True, key="profile_sign_out", use_container_width=True)
        st.caption("Sign Out: Coming Soon")
        return

    if st.button("←  Profile Settings", key="profile_menu_back", use_container_width=True):
        st.session_state["profile_menu_section"] = None
        st.rerun()
    st.markdown(f"<div class='profile-section-title'>{sections[selected][0]} {selected}</div>", unsafe_allow_html=True)
    sections[selected][1]()
