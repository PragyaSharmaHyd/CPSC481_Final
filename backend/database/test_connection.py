from connection import get_connection


def test_connection():
    conn = get_connection()

    movies = conn.execute("""
        SELECT movie_id, title, year
        FROM movies
        LIMIT 5
    """).fetchall()

    for movie in movies:
        print(dict(movie))

    conn.close()


if __name__ == "__main__":
    test_connection()