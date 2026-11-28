import pandas as pd
import numpy as np
from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from database.connection import get_connection


class RecommendationService:

    def __init__(self):
        self.movies_df = None
        self.tfidf_matrix = None
        self.movie_index = {}

        self.load_model()

    def load_model(self):
        """Load movie data and build the TF-IDF model."""

        conn = get_connection()

        query = """
        SELECT
            m.movie_id,
            m.title,
            m.year,
            m.genres,
            COALESCE(GROUP_CONCAT(t.tag, ' '), '') AS tags
        FROM movies m
        LEFT JOIN tags t ON m.movie_id = t.movie_id
        GROUP BY m.movie_id
        ORDER BY m.movie_id
        """

        try:
            self.movies_df = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        # Clean missing values
        self.movies_df["genres"] = (
            self.movies_df["genres"].fillna("")
        )

        self.movies_df["tags"] = (
            self.movies_df["tags"].fillna("")
        )

        # Prepare genres
        self.movies_df["genres_clean"] = (
            self.movies_df["genres"]
            .str.replace("|", " ", regex=False)
            .str.lower()
            .str.strip()
        )

        # Prepare tags
        self.movies_df["tags_clean"] = (
            self.movies_df["tags"]
            .str.lower()
            .str.strip()
        )

        # Keep each cleaned genre as a distinct token, including hyphenated names.
        genre_vectorizer = TfidfVectorizer(
            tokenizer=str.split,
            token_pattern=None,
        )
        genre_matrix = genre_vectorizer.fit_transform(
            self.movies_df["genres_clean"]
        )

        tag_vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        )
        tag_matrix = tag_vectorizer.fit_transform(
            self.movies_df["tags_clean"]
        )

        self.tfidf_matrix = normalize(
            hstack([0.4 * genre_matrix, 0.6 * tag_matrix]).tocsr()
        )

        # Map movie IDs to their matrix row indices
        self.movie_index = {
            movie_id: index
            for index, movie_id in enumerate(
                self.movies_df["movie_id"]
            )
        }

        print("Recommendation model loaded successfully!")
        print(f"Movies loaded: {len(self.movies_df)}")
        print(f"TF-IDF matrix shape: {self.tfidf_matrix.shape}")

    def recommend_similar_movies(self, movie_id, top_n=10):
        """Return the most similar movies for a movie ID."""
        if top_n < 1:
            raise ValueError("top_n must be at least 1")

        movie_pos = self.movie_index.get(movie_id)
        if movie_pos is None:
            return None

        scores = cosine_similarity(
            self.tfidf_matrix[movie_pos], self.tfidf_matrix
        ).flatten()
        scores[movie_pos] = -np.inf

        result_count = min(top_n, len(scores) - 1)
        top_indices = np.argsort(scores)[::-1][:result_count]

        recommendations = self.movies_df.iloc[top_indices][
            ["movie_id", "title", "genres_clean", "tags_clean"]
        ].copy()
        recommendations["similarity_score"] = scores[top_indices]
        return recommendations.to_dict(orient="records")
