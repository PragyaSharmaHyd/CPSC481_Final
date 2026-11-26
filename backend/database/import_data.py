import sqlite3
import pandas as pd
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = Path(__file__).resolve().parent

DATA_DIR = PROJECT_DIR / "data" / "processed"
DB_PATH = DATABASE_DIR / "cinematch.db"


def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)
    print(f"Loaded {filename}: {len(df)} rows")

    return df


def clean_value(value):
    """Convert pandas NaN values to None for SQLite."""
    if pd.isna(value):
        return None

    return value


def import_data():
    # Load datasets
    movies = load_csv("clean_movies.csv")
    ratings = load_csv("clean_ratings.csv")
    tags = load_csv("clean_tags.csv")
    links = load_csv("clean_links.csv")

    conn = sqlite3.connect(DB_PATH)

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        with conn:

            # 1. Import Movies
            movie_records = []

            for _, row in movies.iterrows():
                movie_records.append((
                    int(row["movieId"]),
                    clean_value(row["title"]),
                    clean_value(row["year"]),
                    clean_value(row["genres"])
                ))

            conn.executemany("""
                INSERT OR REPLACE INTO movies
                (movie_id, title, year, genres)
                VALUES (?, ?, ?, ?)
            """, movie_records)

            print(f"Imported {len(movie_records)} movies")

            # 2. Import Users
            user_ids = set(ratings["userId"].dropna().unique())
            user_ids.update(tags["userId"].dropna().unique())

            user_records = [(int(user_id),) for user_id in user_ids]

            conn.executemany("""
                INSERT OR IGNORE INTO users (user_id)
                VALUES (?)
            """, user_records)

            print(f"Imported {len(user_records)} users")


            # 3. Import Ratings
            rating_records = []

            for _, row in ratings.iterrows():
                rating_records.append((
                    int(row["userId"]),
                    int(row["movieId"]),
                    float(row["rating"]),
                    clean_value(row.get("timestamp"))
                ))

            conn.executemany("""
                INSERT OR REPLACE INTO ratings
                (user_id, movie_id, rating, timestamp)
                VALUES (?, ?, ?, ?)
            """, rating_records)

            print(f"Imported {len(rating_records)} ratings")


            # 4. Import Tags
            tag_records = []

            for _, row in tags.iterrows():
                tag_records.append((
                    int(row["userId"]),
                    int(row["movieId"]),
                    clean_value(row["tag"]),
                    clean_value(row.get("timestamp"))
                ))

            conn.executemany("""
                INSERT INTO tags
                (user_id, movie_id, tag, timestamp)
                VALUES (?, ?, ?, ?)
            """, tag_records)

            print(f"Imported {len(tag_records)} tags")


            # -------------------------
            # 5. Import Links
            # -------------------------
            link_records = []

            for _, row in links.iterrows():
                imdb_id = clean_value(row["imdbId"])
                tmdb_id = clean_value(row["tmdbId"])

                # IMDb IDs are stored as strings
                if imdb_id is not None:
                    imdb_id = str(int(imdb_id)).zfill(7)

                if tmdb_id is not None:
                    tmdb_id = int(tmdb_id)

                link_records.append((
                    int(row["movieId"]),
                    imdb_id,
                    tmdb_id
                ))

            conn.executemany("""
                INSERT OR REPLACE INTO links
                (movie_id, imdb_id, tmdb_id)
                VALUES (?, ?, ?)
            """, link_records)

            print(f"Imported {len(link_records)} links")

    except Exception as e:
        print(f"Error importing data: {e}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    import_data()