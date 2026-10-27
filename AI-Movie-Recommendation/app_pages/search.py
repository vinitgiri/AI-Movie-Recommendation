"""
app_pages/search.py
--------------------
CineAI Search & Movie Explorer Page — Instant search, genre filtering,
and catalog discovery across 3,883 MovieLens titles.
"""

from __future__ import annotations

import streamlit as st

from src.components.styles import inject_global_css
from src.components.navbar import render_navbar, render_footer
from src.components.model_loader import load_models, models_missing_error
from src.components.movie_card import render_movie_card_with_actions, strip_year

inject_global_css()
render_navbar("Search")

movies, ratings, users, hybrid_model, collab_model, missing = load_models()
if missing:
    models_missing_error(missing)
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.8rem;">
    <div class="section-eyebrow">EXPLORE CATALOG</div>
    <div class="section-headline">Search & Browse Movies</div>
    <div class="section-subheadline">
        Search across 3,883 movies by title, filter by genre, and explore detailed AI profiles.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Search & Filter Controls ──────────────────────────────────────────────────
search_c1, search_c2, search_c3 = st.columns([3, 1.5, 1.5], gap="medium")

with search_c1:
    search_query = st.text_input(
        "Search Title",
        placeholder="Type movie name (e.g. Matrix, Star Wars, Toy Story)...",
        key="search_input_box",
        label_visibility="collapsed",
    )

with search_c2:
    GENRES = [
        "All Genres", "Action", "Adventure", "Animation", "Children's",
        "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
        "Sci-Fi", "Thriller", "War", "Western",
    ]
    saved_genre = st.session_state.get("search_genre_filter", "All Genres")
    if saved_genre not in GENRES and f"{saved_genre}" in GENRES:
        saved_genre = f"{saved_genre}"
    genre_idx = GENRES.index(saved_genre) if saved_genre in GENRES else 0

    selected_genre = st.selectbox(
        "Filter Genre",
        GENRES,
        index=genre_idx,
        key="search_genre_select",
        label_visibility="collapsed",
    )
    st.session_state["search_genre_filter"] = selected_genre

with search_c3:
    sort_by = st.selectbox(
        "Sort Order",
        ["Title (A-Z)", "Title (Z-A)", "Most Rated"],
        index=0,
        key="search_sort_select",
        label_visibility="collapsed",
    )

# ── Query Filtering ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_filtered_movies(query: str, genre: str, sort_mode: str, limit: int = 40):
    df = movies.copy()

    if genre and genre != "All Genres":
        df = df[df["genres"].str.contains(genre, case=False, na=False)]

    if query and query.strip():
        df = df[df["title"].str.contains(query.strip(), case=False, na=False)]

    if sort_mode == "Title (A-Z)":
        df = df.sort_values("title", ascending=True)
    elif sort_mode == "Title (Z-A)":
        df = df.sort_values("title", ascending=False)
    elif sort_mode == "Most Rated":
        # Merge rating counts
        counts = ratings.groupby("movieId")["rating"].count().reset_index()
        counts.columns = ["movieId", "rating_count"]
        df = df.merge(counts, on="movieId", how="left").fillna(0)
        df = df.sort_values("rating_count", ascending=False)

    return df.head(limit)

filtered_df = get_filtered_movies(search_query, selected_genre, sort_by)

st.markdown(f"""
<div style="font-size:0.85rem;color:#8A8A8A;margin: 0.5rem 0 1.5rem;">
    Showing <strong>{len(filtered_df)}</strong> movies
    {f'matching "<strong>{search_query}</strong>"' if search_query else ''}
    {f'in <strong>{selected_genre}</strong>' if selected_genre != "All Genres" else ''}
</div>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.markdown("""
    <div style="text-align:center;padding:4rem 1rem;color:#666;">
        <div style="font-size:3rem;margin-bottom:0.8rem;">🔍</div>
        <div style="font-size:1.2rem;font-weight:700;color:#FFF;margin-bottom:0.3rem;">No Movies Found</div>
        <div style="font-size:0.85rem;color:#8A8A8A;">Try adjusting your search query or selecting a different genre.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    COLS_COUNT = 5
    cols = st.columns(COLS_COUNT, gap="small")
    for i, (_, row) in enumerate(filtered_df.iterrows()):
        col = cols[i % COLS_COUNT]
        with col:
            title = row.get("title", "")
            render_movie_card_with_actions(
                row_or_title=row,
                idx_key=f"search_{i}_{title[:8]}",
            )

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
render_footer()
