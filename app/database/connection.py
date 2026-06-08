import psycopg2
import psycopg2.pool

from app.core.config import DATABASE_URL


class DatabaseConnection:
    _pool: psycopg2.pool.ThreadedConnectionPool = None

    @classmethod
    def _getPool(cls) -> psycopg2.pool.ThreadedConnectionPool:
        if cls._pool is None:
            cls._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=DATABASE_URL
            )
        return cls._pool

    @classmethod
    def getconn(cls):
        return cls._getPool().getconn()

    @classmethod
    def putconn(cls, conn) -> None:
        cls._getPool().putconn(conn)
