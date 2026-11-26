import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "cinematch.db"

conn = sqlite3.connect(DB_PATH)

tables = ["movies", "users", "ratings", "tags", "links"]

print("DATABASE ROW COUNTS\n")

for table in tables:
    count = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count:,} rows")

# checking if the first 5 rows of each table are present
print("\nSAMPLE MOVIES\n")

movies = conn.execute("""
    SELECT movie_id, title, year, genres
    FROM movies
    LIMIT 5
""").fetchall()

for movie in movies:
    print(movie)


print("\nSAMPLE RATINGS\n")

ratings = conn.execute("""
    SELECT user_id, movie_id, rating
    FROM ratings
    LIMIT 5
""").fetchall()

for rating in ratings:
    print(rating)


print("\nSAMPLE TAGS\n")

tags = conn.execute("""
    SELECT user_id, movie_id, tag
    FROM tags
    LIMIT 5
""").fetchall()

for tag in tags:
    print(tag)


conn = sqlite3.connect(DB_PATH)

movie_id = 1

result = conn.execute("""
    SELECT
        m.title,
        m.year,
        m.genres,
        r.rating,
        t.tag,
        l.imdb_id,
        l.tmdb_id

    FROM movies m

    LEFT JOIN ratings r
        ON m.movie_id = r.movie_id

    LEFT JOIN tags t
        ON m.movie_id = t.movie_id

    LEFT JOIN links l
        ON m.movie_id = l.movie_id

    WHERE m.movie_id = ?
""", (movie_id,)).fetchall()

for row in result:
    print(row)

conn.close()