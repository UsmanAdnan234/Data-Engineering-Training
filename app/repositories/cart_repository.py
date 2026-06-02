import sqlite3


class CartRepository:

    def __init__(self, conn):
        self.conn = conn

    def get_user(self, user_id: int):

        cursor = self.conn.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        return cursor.fetchone()

    def get_cart_by_user(self, user_id: int):

        cursor = self.conn.execute(
            """
            SELECT cart_id, user_id, status
            FROM carts
            WHERE user_id = ?
            AND status = 'active'
            """,
            (user_id,)
        )

        return cursor.fetchone()

    def get_cart(self, cart_id: int):

        cursor = self.conn.execute(
            """
            SELECT cart_id, user_id, status
            FROM carts
            WHERE cart_id = ?
            """,
            (cart_id,)
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

    def delete_cart(self, cart_id: int):

        cursor = self.conn.execute(
            """
            DELETE FROM carts
            WHERE cart_id = ?
            """,
            (cart_id,)
        )

        self.conn.commit()

        return cursor.rowcount

    def checkout_cart(self, cart_id: int):

        cursor = self.conn.execute(
            """
            UPDATE carts
            SET status = 'checked_out'
            WHERE cart_id = ?
            """,
            (cart_id,)
        )

        self.conn.commit()

        return cursor.rowcount

    def get_variant(self, variant_id: int):

        cursor = self.conn.execute(
            """
            SELECT variant_id
            FROM product_variants
            WHERE variant_id = ?
            """,
            (variant_id,)
        )

        return cursor.fetchone()

    def get_cart_item(self, cart_id: int, variant_id: int):

        cursor = self.conn.execute(
            """
            SELECT item_id, quantity
            FROM cart_items
            WHERE cart_id = ?
            AND variant_id = ?
            """,
            (cart_id, variant_id)
        )

        return cursor.fetchone()

    def get_item_in_cart(self, item_id: int, cart_id: int):

        cursor = self.conn.execute(
            """
            SELECT item_id
            FROM cart_items
            WHERE item_id = ?
            AND cart_id = ?
            """,
            (item_id, cart_id)
        )

        return cursor.fetchone()

    def cart_has_items(self, cart_id: int) -> bool:

        cursor = self.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM cart_items
            WHERE cart_id = ?
            """,
            (cart_id,)
        )

        row = cursor.fetchone()

        return row["count"] > 0

    def add_item(self, cart_id: int, variant_id: int, quantity: int):

        cursor = self.conn.execute(
            """
            INSERT INTO cart_items (cart_id, variant_id, quantity)
            VALUES (?, ?, ?)
            """,
            (cart_id, variant_id, quantity)
        )

        self.conn.commit()

        return cursor.lastrowid

    def update_quantity(self, item_id: int, quantity: int):

        cursor = self.conn.execute(
            """
            UPDATE cart_items
            SET quantity = ?
            WHERE item_id = ?
            """,
            (quantity, item_id)
        )

        self.conn.commit()

        return cursor.rowcount

    def delete_cart_item(self, item_id: int):

        cursor = self.conn.execute(
            """
            DELETE FROM cart_items
            WHERE item_id = ?
            """,
            (item_id,)
        )

        self.conn.commit()

        return cursor.rowcount

    def clear_cart(self, cart_id: int):

        cursor = self.conn.execute(
            """
            DELETE FROM cart_items
            WHERE cart_id = ?
            """,
            (cart_id,)
        )

        self.conn.commit()

        return cursor.rowcount

    def close(self):
        self.conn.close()
