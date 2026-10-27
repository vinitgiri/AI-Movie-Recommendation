"""Load the refreshed TMDB catalog for catalog-facing UI pages."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src import config

CATALOG_PATH = config.BASE_DIR / "data" / "tmdb_movies.csv"


@st.cache_data(show_spinner=False)
def load_tmdb_catalog() -> pd.DataFrame:
    """Return the local TMDB catalog in the columns expected by movie cards."""
    if not CATALOG_PATH.exists():
        return pd.DataFrame(columns=["tmdb_id", "title", "genres"])

    catalog = pd.read_csv(CATALOG_PATH, dtype={"tmdb_id": "Int64"}).fillna("")
    catalog = catalog.drop_duplicates(subset=["tmdb_id"])
    catalog = catalog.drop_duplicates(subset=["title"], keep="first")
    catalog["release_year"] = catalog["release_date"].astype(str).str[:4]
    catalog["title"] = catalog.apply(
        lambda row: f"{row['title']} ({row['release_year']})"
        if row["release_year"].isdigit()
        else str(row["title"]),
        axis=1,
    )
    return catalog.reset_index(drop=True)
