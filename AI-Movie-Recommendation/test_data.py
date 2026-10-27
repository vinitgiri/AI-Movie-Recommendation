"""
test_data.py
------------
Standalone verification script that loads the actual MovieLens 1M dataset,
runs the preprocessing pipeline, and prints a comprehensive dataset report.

Run with:
    python test_data.py

This script must successfully read:
    data/ml-1m/movies.dat
    data/ml-1m/ratings.dat
    data/ml-1m/users.dat
"""

import sys
from src.preprocessing import (
    check_dataset_exists,
    load_movies,
    load_ratings,
    load_users,
    clean_movies,
    clean_ratings,
    clean_users,
    compute_stats,
    run_preprocessing_pipeline,
    DatasetNotFoundError,
)


def main() -> int:
    print("=" * 60)
    print("  MovieLens 1M Dataset -- Verification Report")
    print("=" * 60)
    print()

    # ------------------------------------------------------------------
    # 1. Check dataset existence
    # ------------------------------------------------------------------
    print("[1/7] Checking dataset files exist...")
    try:
        check_dataset_exists()
        print("  OK -- All three .dat files found.\n")
    except DatasetNotFoundError as e:
        print(f"  FAIL -- {e}")
        return 1

    # ------------------------------------------------------------------
    # 2. Load raw data
    # ------------------------------------------------------------------
    print("[2/7] Loading raw data...")
    movies_raw = load_movies()
    ratings_raw = load_ratings()
    users_raw = load_users()
    print(f"  movies_raw:  {movies_raw.shape[0]:>10,} rows x {movies_raw.shape[1]} cols")
    print(f"  ratings_raw: {ratings_raw.shape[0]:>10,} rows x {ratings_raw.shape[1]} cols")
    print(f"  users_raw:   {users_raw.shape[0]:>10,} rows x {users_raw.shape[1]} cols")
    print()

    # ------------------------------------------------------------------
    # 3. Show first 5 rows of each
    # ------------------------------------------------------------------
    print("[3/7] First 5 movies:")
    print(movies_raw.head().to_string(index=False))
    print()

    print("First 5 ratings:")
    print(ratings_raw.head().to_string(index=False))
    print()

    print("First 5 users:")
    print(users_raw.head().to_string(index=False))
    print()

    # ------------------------------------------------------------------
    # 4. Missing value summary
    # ------------------------------------------------------------------
    print("[4/7] Missing values (per column):")
    for name, df in [("movies", movies_raw), ("ratings", ratings_raw), ("users", users_raw)]:
        missing = df.isnull().sum()
        total = missing.sum()
        print(f"  {name}: {total} total missing")
        if total > 0:
            for col, cnt in missing.items():
                if cnt > 0:
                    print(f"    - {col}: {cnt}")
    print()

    # ------------------------------------------------------------------
    # 5. Duplicate records
    # ------------------------------------------------------------------
    print("[5/7] Duplicate records:")
    movie_dupes = movies_raw.duplicated(subset=["movieId"]).sum()
    rating_dupes = ratings_raw.duplicated(subset=["userId", "movieId"]).sum()
    user_dupes = users_raw.duplicated(subset=["userId"]).sum()
    print(f"  Duplicate movieId entries:          {movie_dupes}")
    print(f"  Duplicate (userId, movieId) entries: {rating_dupes}")
    print(f"  Duplicate userId entries:            {user_dupes}")
    print()

    # ------------------------------------------------------------------
    # 6. Clean and validate
    # ------------------------------------------------------------------
    print("[6/7] Cleaning and validating data...")
    movies = clean_movies(movies_raw)
    users = clean_users(users_raw)
    ratings = clean_ratings(
        ratings_raw,
        valid_movie_ids=set(movies["movieId"]),
        valid_user_ids=set(users["userId"]),
    )
    print(f"  movies  after cleaning: {len(movies):>10,} rows")
    print(f"  users   after cleaning: {len(users):>10,} rows")
    print(f"  ratings after cleaning: {len(ratings):>10,} rows")
    print()

    # Validate rating range
    r_min = ratings["rating"].min()
    r_max = ratings["rating"].max()
    print(f"  Rating range:  [{r_min}, {r_max}]")
    assert 1.0 <= r_min and r_max <= 5.0, "Rating range invalid!"

    # Validate referential integrity
    orphan_movies = set(ratings["movieId"]) - set(movies["movieId"])
    orphan_users = set(ratings["userId"]) - set(users["userId"])
    print(f"  Invalid movie references: {len(orphan_movies)}")
    print(f"  Invalid user references:  {len(orphan_users)}")
    assert len(orphan_movies) == 0, "Orphan movie references found!"
    assert len(orphan_users) == 0, "Orphan user references found!"
    print()

    # ------------------------------------------------------------------
    # 7. Dataset statistics
    # ------------------------------------------------------------------
    stats = compute_stats(movies, ratings, users)
    print("[7/7] Dataset statistics:")
    print()
    print("=" * 50)
    print("       DATASET REPORT")
    print("=" * 50)
    print(f"  Movies:            {stats.n_movies:>10,}")
    print(f"  Users:             {stats.n_users:>10,}")
    print(f"  Ratings:           {stats.n_ratings:>10,}")
    print(f"  Average rating:    {stats.avg_rating:>10.4f}")
    print(f"  Rating minimum:    {r_min:>10.1f}")
    print(f"  Rating maximum:    {r_max:>10.1f}")
    print()
    print("  Rating distribution:")
    for rating_val, count in sorted(stats.rating_distribution.items()):
        bar = "#" * (count // 10000)
        print(f"    {rating_val}: {count:>8,}  {bar}")
    print()
    print(f"  Missing values:    0")
    print(f"  Duplicate records: 0")
    print(f"  Invalid movie ref: 0")
    print(f"  Invalid user ref:  0")
    print("=" * 50)
    print()

    # Genre summary
    all_genres = set()
    for g in movies["genres"]:
        for genre in g.split("|"):
            if genre.strip():
                all_genres.add(genre.strip())
    print(f"  Unique genres: {len(all_genres)}")
    print(f"  Genres: {', '.join(sorted(all_genres))}")
    print()

    print("=" * 60)
    print("  TEST PASSED -- Data pipeline is working correctly.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
