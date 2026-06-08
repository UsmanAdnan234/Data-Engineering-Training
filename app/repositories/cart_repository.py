import psycopg2
import psycopg2.extras
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
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params)
            return cur
        except psycopg2.OperationalError as e:
            raise DatabaseException(f"Operational error: {e}")
        except psycopg2.IntegrityError as e:
            raise DatabaseException(f"Integrity error: {e}")
        except psycopg2.Error as e:
            raise DatabaseException(f"Database error: {e}")

    def getUser(self, userId: int):
        cur = self._execute(
            "SELECT user_id FROM users WHERE user_id = %s",
            (userId,)
        )
        return cur.fetchone()

    def getActiveCartByUser(self, userId: int):
        cur = self._execute(
            """
            SELECT cart_id, user_id, status
            FROM carts
            WHERE user_id = %s
            AND status = 'active'
            """,
            (userId,)
        )
        return cur.fetchone()

    def getCart(self, cartId: int):
        cur = self._execute(
            """
            SELECT cart_id, user_id, status
            FROM carts
            WHERE cart_id = %s
            """,
            (cartId,)
        )
        return cur.fetchone()

    def createCart(self, userId: int):
        cur = self._execute(
            "INSERT INTO carts(user_id) VALUES(%s) RETURNING cart_id",
            (userId,)
        )
        self._conn.commit()
        return cur.fetchone()["cart_id"]

    def deleteCart(self, cartId: int):
        cur = self._execute(
            "DELETE FROM carts WHERE cart_id = %s",
            (cartId,)
        )
        self._conn.commit()
        return cur.rowcount

    def checkoutCart(self, cartId: int):
        cur = self._execute(
            "UPDATE carts SET status = 'checked_out' WHERE cart_id = %s",
            (cartId,)
        )
        self._conn.commit()
        return cur.rowcount

    def getVariant(self, variantId: int):
        cur = self._execute(
            "SELECT variant_id, stock FROM product_variants WHERE variant_id = %s",
            (variantId,)
        )
        return cur.fetchone()

    def getCartItem(self, cartId: int, variantId: int):
        cur = self._execute(
            """
            SELECT item_id, quantity
            FROM cart_items
            WHERE cart_id = %s AND variant_id = %s
            """,
            (cartId, variantId)
        )
        return cur.fetchone()

    def getItemInCart(self, itemId: int, cartId: int):
        cur = self._execute(
            """
            SELECT item_id
            FROM cart_items
            WHERE item_id = %s AND cart_id = %s
            """,
            (itemId, cartId)
        )
        return cur.fetchone()

    def cartHasItems(self, cartId: int) -> bool:
        cur = self._execute(
            "SELECT COUNT(*) AS count FROM cart_items WHERE cart_id = %s",
            (cartId,)
        )
        row = cur.fetchone()
        return row["count"] > 0

    def addItem(self, cartId: int, variantId: int, quantity: int):
        cur = self._execute(
            """
            INSERT INTO cart_items (cart_id, variant_id, quantity)
            VALUES (%s, %s, %s)
            RETURNING item_id
            """,
            (cartId, variantId, quantity)
        )
        self._conn.commit()
        return cur.fetchone()["item_id"]

    def updateQuantity(self, itemId: int, quantity: int):
        cur = self._execute(
            "UPDATE cart_items SET quantity = %s WHERE item_id = %s",
            (quantity, itemId)
        )
        self._conn.commit()
        return cur.rowcount

    def deleteCartItem(self, itemId: int):
        cur = self._execute(
            "DELETE FROM cart_items WHERE item_id = %s",
            (itemId,)
        )
        self._conn.commit()
        return cur.rowcount

    def reduceStock(self, cartId: int):
        cur = self._execute(
            """
            UPDATE product_variants
            SET stock = stock - (
                SELECT quantity FROM cart_items
                WHERE variant_id = product_variants.variant_id
                AND cart_id = %s
            )
            WHERE variant_id IN (
                SELECT variant_id FROM cart_items WHERE cart_id = %s
            )
            """,
            (cartId, cartId)
        )
        self._conn.commit()
        return cur.rowcount
