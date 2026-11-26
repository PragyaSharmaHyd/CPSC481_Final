import sqlite3
from pathlib import Path

# Get the database directory
BASE_DIR = Path(__file__).resolve().parent

# Database file path
DB_PATH = BASE_DIR / "cinematch.db"

# Schema file path
SCHEMA_PATH = BASE_DIR / "schema.sql"


def initialize_database():
    connection = sqlite3.connect(DB_PATH)

    try:
        with open(SCHEMA_PATH, "r") as file:
            schema = file.read()

        connection.executescript(schema)

        print("Database created successfully!")
        print(f"Database location: {DB_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()