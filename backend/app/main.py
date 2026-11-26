from fastapi import FastAPI

app = FastAPI(
    title="CineMatch API",
    description="Movie recommendation backend",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to CineMatch API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}