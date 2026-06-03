import sqlite3
import threading

from app.core.config import DB_NAME


class DatabaseConnection:
    """
    Thread-local singleton. Each thread gets one connection that is reused
    across all requests on that thread — no open/close per request.
    """
    _local = threading.local()

    @classmethod
    def getInstance(cls):
        if not hasattr(cls._local, "conn") or cls._local.conn is None:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            cls._local.conn = conn
        return cls._local.conn
