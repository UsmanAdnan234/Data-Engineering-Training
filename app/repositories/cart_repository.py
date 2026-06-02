import sqlite3


class CartRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_user(self, user_id: int):

        cursor = self.conn.execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        )

        return cursor.fetchone()

    def get_cart_by_user(self, user_id: int):

        cursor = self.conn.execute(
            "SELECT cart_id FROM carts WHERE user_id = ?",
            (user_id,)
        )

        return cursor.fetchone()

    def create_cart(self, user_id: int):

        cursor = self.conn.execute(
            """
            INSERT INTO carts(user_id)
            VALUES(?)
            """,
            (user_id,)
        )

        self.conn.commit()

        return cursor.lastrowid