from app.repositories.cart_repository import CartRepository
from app.core.exceptions import (
    UserNotFoundException,
    CartAlreadyExistsException
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