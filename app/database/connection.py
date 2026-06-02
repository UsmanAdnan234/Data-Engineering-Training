import sqlite3

from app.core.config import DB_NAME


def get_connection():
    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    return conn