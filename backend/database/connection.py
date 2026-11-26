import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "cinematch.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)

    # Return rows in a dictionary-like format
    conn.row_factory = sqlite3.Row

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    return conn