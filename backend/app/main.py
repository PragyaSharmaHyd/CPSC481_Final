import json
from urllib import response

import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.routes.movies import router as movies_router

app = FastAPI(
    title="CineMatch API",
    description="Movie recommendation backend",
    version="1.0.0"
)

app.include_router(movies_router)

# Locate processed movies dataset
ROOT_DIR = Path(__file__).resolve().parents[2]

print("Project root", ROOT_DIR)

MOVIES_PATH = ROOT_DIR / "data" / "processed" / "clean_movies.csv"
RATINGS_PATH = ROOT_DIR / "data" / "processed" / "clean_ratings.csv"
TAGS_PATH = ROOT_DIR / "data" / "processed" / "clean_tags.csv"

# loading the movies dataset
movies_df = pd.read_csv(MOVIES_PATH)
ratings_df = pd.read_csv(RATINGS_PATH)
tags_df = pd.read_csv(TAGS_PATH)

@app.get("/")
def home():
    return {"message": "Welcome to CineMatch API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# exceute the following get function to get the movies dataset in json format
@app.get("/movies")
def get_movies():
        return json.loads(movies_df.to_json(orient="records"))

# exceute the following get function to search for movies by title in json format
@app.get("/movies/search")
def search_movies(query: str):
    results = movies_df[movies_df["title"].str.contains(
        query, case=False, na=False, regex=False
    )]
    return json.loads(results.to_json(orient="records"))

# exceute the following get function to get the movie by id in json format
@app.get("/movies/{movie_id}")
def get_movie_details(movie_id: int):

    # Find the movie
    movie = movies_df[movies_df["movieId"] == movie_id]

    if movie.empty:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    # Get ratings for this movie
    movie_ratings = ratings_df[
        ratings_df["movieId"] == movie_id
    ]

    # Get tags for this movie
    movie_tags = tags_df[
        tags_df["movieId"] == movie_id
    ]

    # Calculate rating statistics
    average_rating = (
        round(movie_ratings["rating"].mean(), 2)
        if not movie_ratings.empty
        else None
    )

    rating_count = len(movie_ratings)

    # Extract movie information
    movie_info = movie.iloc[0].to_dict()

    # Build response
    response = {
        "movie": json.loads(
            movie.to_json(orient="records")
        )[0],

        "ratings": {
            "average": average_rating,
            "count": rating_count,
            "individual_ratings": json.loads(
                movie_ratings[
                    ["userId", "rating"]
                ].to_json(orient="records")
            )
        },

        "tags": json.loads(
            movie_tags[
                ["userId", "tag"]
            ].to_json(orient="records")
        )
    } 
    
    return response
    
@app.get("/recommendations/{movie_id}")
def get_recommendations(movie_id: int):
    # Placeholder for recommendation logic - replace with actual recommendation implementation
    return {"message": "Recommendations for movie ID: {movie_id}".format(movie_id=movie_id)}
