from app.repositories.cart_repository import CartRepository
from app.core.exceptions import (
    UserNotFoundException,
    CartAlreadyExistsException,
    CartNotFoundException,
    CartAlreadyCheckedOutException,
    CartEmptyException,
    VariantNotFoundException,
    CartItemNotFoundException,
)


class CartService:

    def __init__(self, conn):
        self.repo = CartRepository(conn)

    def create_cart(self, user_id: int):

        user = self.repo.get_user(user_id)

        if not user:
            raise UserNotFoundException()

        cart = self.repo.get_cart_by_user(user_id)

        if cart:
            raise CartAlreadyExistsException()

        cart_id = self.repo.create_cart(user_id)

        return {
            "cart_id": cart_id,
            "user_id": user_id
        }

    def add_item(self, cart_id: int, variant_id: int, quantity: int):

        cart = self.repo.get_cart(cart_id)

        if not cart:
            raise CartNotFoundException()

        if cart["status"] == "checked_out":
            raise CartAlreadyCheckedOutException()

        variant = self.repo.get_variant(variant_id)

        if not variant:
            raise VariantNotFoundException()

        existing = self.repo.get_cart_item(cart_id, variant_id)

        if existing:
            new_quantity = existing["quantity"] + quantity
            self.repo.update_quantity(existing["item_id"], new_quantity)
            return {
                "item_id": existing["item_id"],
                "cart_id": cart_id,
                "variant_id": variant_id,
                "quantity": new_quantity
            }

        item_id = self.repo.add_item(cart_id, variant_id, quantity)

        return {
            "item_id": item_id,
            "cart_id": cart_id,
            "variant_id": variant_id,
            "quantity": quantity
        }

    def remove_item(self, cart_id: int, item_id: int):

        cart = self.repo.get_cart(cart_id)

        if not cart:
            raise CartNotFoundException()

        if cart["status"] == "checked_out":
            raise CartAlreadyCheckedOutException()

        item = self.repo.get_item_in_cart(item_id, cart_id)

        if not item:
            raise CartItemNotFoundException(f"Item id {item_id} not found in cart {cart_id}")

        self.repo.delete_cart_item(item_id)

    def delete_cart(self, cart_id: int):

        cart = self.repo.get_cart(cart_id)

        if not cart:
            raise CartNotFoundException()

        self.repo.delete_cart(cart_id)

    def checkout(self, cart_id: int):

        cart = self.repo.get_cart(cart_id)

        if not cart:
            raise CartNotFoundException()

        if cart["status"] == "checked_out":
            raise CartAlreadyCheckedOutException()

        if not self.repo.cart_has_items(cart_id):
            raise CartEmptyException()

        self.repo.checkout_cart(cart_id)

        return {
            "cart_id": cart_id,
            "status": "checked_out"
        }
