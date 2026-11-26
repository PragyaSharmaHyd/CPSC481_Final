
from fastapi import APIRouter, Query
from database.connection import get_connection

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get("/")
def get_movies(
    search: str | None = None,
    genre: str | None = None,
    year: int | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    conn = get_connection()

    try:
        query = "SELECT * FROM movies WHERE 1=1"
        params = []

        # Search movie titles
        if search:
            query += " AND title LIKE ?"
            params.append(f"%{search}%")

        # Filter by genre
        if genre:
            query += """
                AND instr(
                    '|' || genres || '|',
                    '|' || ? || '|'
                ) > 0
            """
            params.append(genre)

        # Filter by year
        if year is not None:
            query += " AND year = ?"
            params.append(year)

        # Count matching movies
        count_query = query.replace(
            "SELECT *",
            "SELECT COUNT(*)",
            1
        )

        total = conn.execute(
            count_query,
            params
        ).fetchone()[0]

        # Pagination
        offset = (page - 1) * limit

        query += " ORDER BY movie_id LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        movies = conn.execute(
            query,
            params
        ).fetchall()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "movies": [dict(movie) for movie in movies]
        }

    finally:
        conn.close()
