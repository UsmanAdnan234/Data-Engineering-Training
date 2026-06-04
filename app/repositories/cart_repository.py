import sqlite3
from abc import ABC, abstractmethod

from app.core.exceptions import DatabaseException


class ICartRepository(ABC):

    @abstractmethod
    def getUser(self, userId: int): ...

    @abstractmethod
    def getActiveCartByUser(self, userId: int): ...

    @abstractmethod
    def getCart(self, cartId: int): ...

    @abstractmethod
    def createCart(self, userId: int): ...

    @abstractmethod
    def deleteCart(self, cartId: int): ...

    @abstractmethod
    def checkoutCart(self, cartId: int): ...

    @abstractmethod
    def getVariant(self, variantId: int): ...

    @abstractmethod
    def getCartItem(self, cartId: int, variantId: int): ...

    @abstractmethod
    def getItemInCart(self, itemId: int, cartId: int): ...

    @abstractmethod
    def cartHasItems(self, cartId: int) -> bool: ...

    @abstractmethod
    def addItem(self, cartId: int, variantId: int, quantity: int): ...

    @abstractmethod
    def updateQuantity(self, itemId: int, quantity: int): ...

    @abstractmethod
    def deleteCartItem(self, itemId: int): ...

    @abstractmethod
    def reduceStock(self, cartId: int): ...


class CartRepository(ICartRepository):

    def __init__(self, conn):
        self._conn = conn

    def _execute(self, query: str, params: tuple = ()):
        try:
            return self._conn.execute(query, params)
        except sqlite3.OperationalError as e:
            raise DatabaseException(f"Operational error: {e}")
        except sqlite3.IntegrityError as e:
            raise DatabaseException(f"Integrity error: {e}")
        except sqlite3.DatabaseError as e:
            raise DatabaseException(f"Database error: {e}")

    def getUser(self, userId: int):
        cursor = self._execute(
            "SELECT user_id FROM users WHERE user_id = ?",
            (userId,)
        )
        return cursor.fetchone()

    def getActiveCartByUser(self, userId: int):
        cursor = self._execute(
            """
            SELECT cart_id, user_id, status
            FROM carts
            WHERE user_id = ?
            AND status = 'active'
            """,
            (userId,)
        )
        return cursor.fetchone()

    def getCart(self, cartId: int):
        cursor = self._execute(
            """
            SELECT cart_id, user_id, status
            FROM carts
            WHERE cart_id = ?
            """,
            (cartId,)
        )
        return cursor.fetchone()

    def createCart(self, userId: int):
        cursor = self._execute(
            "INSERT INTO carts(user_id) VALUES(?)",
            (userId,)
        )
        self._conn.commit()
        return cursor.lastrowid

    def deleteCart(self, cartId: int):
        cursor = self._execute(
            "DELETE FROM carts WHERE cart_id = ?",
            (cartId,)
        )
        self._conn.commit()
        return cursor.rowcount

    def checkoutCart(self, cartId: int):
        cursor = self._execute(
            "UPDATE carts SET status = 'checked_out' WHERE cart_id = ?",
            (cartId,)
        )
        self._conn.commit()
        return cursor.rowcount

    def getVariant(self, variantId: int):
        cursor = self._execute(
            "SELECT variant_id, stock FROM product_variants WHERE variant_id = ?",
            (variantId,)
        )
        return cursor.fetchone()

    def getCartItem(self, cartId: int, variantId: int):
        cursor = self._execute(
            """
            SELECT item_id, quantity
            FROM cart_items
            WHERE cart_id = ? AND variant_id = ?
            """,
            (cartId, variantId)
        )
        return cursor.fetchone()

    def getItemInCart(self, itemId: int, cartId: int):
        cursor = self._execute(
            """
            SELECT item_id
            FROM cart_items
            WHERE item_id = ? AND cart_id = ?
            """,
            (itemId, cartId)
        )
        return cursor.fetchone()

    def cartHasItems(self, cartId: int) -> bool:
        cursor = self._execute(
            "SELECT COUNT(*) AS count FROM cart_items WHERE cart_id = ?",
            (cartId,)
        )
        row = cursor.fetchone()
        return row["count"] > 0

    def addItem(self, cartId: int, variantId: int, quantity: int):
        cursor = self._execute(
            """
            INSERT INTO cart_items (cart_id, variant_id, quantity)
            VALUES (?, ?, ?)
            """,
            (cartId, variantId, quantity)
        )
        self._conn.commit()
        return cursor.lastrowid

    def updateQuantity(self, itemId: int, quantity: int):
        cursor = self._execute(
            "UPDATE cart_items SET quantity = ? WHERE item_id = ?",
            (quantity, itemId)
        )
        self._conn.commit()
        return cursor.rowcount

    def deleteCartItem(self, itemId: int):
        cursor = self._execute(
            "DELETE FROM cart_items WHERE item_id = ?",
            (itemId,)
        )
        self._conn.commit()
        return cursor.rowcount

    def reduceStock(self, cartId: int):
        cursor = self._execute(
            """
            UPDATE product_variants
            SET stock = stock - (
                SELECT quantity FROM cart_items
                WHERE variant_id = product_variants.variant_id
                AND cart_id = ?
            )
            WHERE variant_id IN (
                SELECT variant_id FROM cart_items WHERE cart_id = ?
            )
            """,
            (cartId, cartId)
        )
        self._conn.commit()
        return cursor.rowcount
