from abc import ABC, abstractmethod

from app.repositories.cart_repository import ICartRepository
from app.core.exceptions import (
    UserNotFoundException,
    CartAlreadyExistsException,
    CartNotFoundException,
    CartAlreadyCheckedOutException,
    CartEmptyException,
    VariantNotFoundException,
    CartItemNotFoundException,
    InsufficientStockException,
)


class ICartService(ABC):

    @abstractmethod
    def createCart(self, userId: int): ...

    @abstractmethod
    def addItem(self, cartId: int, variantId: int, quantity: int): ...

    @abstractmethod
    def removeItem(self, cartId: int, itemId: int): ...

    @abstractmethod
    def deleteCart(self, cartId: int): ...

    @abstractmethod
    def checkout(self, cartId: int): ...


class CartService(ICartService):

    def __init__(self, repo: ICartRepository):
        self._repo = repo

    def createCart(self, userId: int):
        user = self._repo.getUser(userId)
        if not user:
            raise UserNotFoundException(f"User with id={userId} not found")

        activeCart = self._repo.getActiveCartByUser(userId)
        if activeCart:
            raise CartAlreadyExistsException(
                f"User id={userId} already has an active cart (cart_id={activeCart['cart_id']})"
            )

        cartId = self._repo.createCart(userId)
        return {"cart_id": cartId, "user_id": userId}

    def addItem(self, cartId: int, variantId: int, quantity: int):
        cart = self._repo.getCart(cartId)
        if not cart:
            raise CartNotFoundException(f"Cart with id={cartId} not found")

        if cart["status"] == "checked_out":
            raise CartAlreadyCheckedOutException(
                f"Cart id={cartId} is already checked out, cannot add items"
            )

        variant = self._repo.getVariant(variantId)
        if not variant:
            raise VariantNotFoundException(f"Product variant with id={variantId} not found")

        existing = self._repo.getCartItem(cartId, variantId)
        if existing:
            newQuantity = existing["quantity"] + quantity
            if newQuantity > variant["stock"]:
                raise InsufficientStockException(
                    f"Requested total quantity={newQuantity} exceeds available stock={variant['stock']}"
                    f" for variant_id={variantId}"
                )
            self._repo.updateQuantity(existing["item_id"], newQuantity)
            return {
                "item_id": existing["item_id"],
                "cart_id": cartId,
                "variant_id": variantId,
                "quantity": newQuantity
            }

        if quantity > variant["stock"]:
            raise InsufficientStockException(
                f"Requested quantity={quantity} exceeds available stock={variant['stock']}"
                f" for variant_id={variantId}"
            )

        itemId = self._repo.addItem(cartId, variantId, quantity)
        return {
            "item_id": itemId,
            "cart_id": cartId,
            "variant_id": variantId,
            "quantity": quantity
        }

    def removeItem(self, cartId: int, itemId: int):
        cart = self._repo.getCart(cartId)
        if not cart:
            raise CartNotFoundException(f"Cart with id={cartId} not found")

        if cart["status"] == "checked_out":
            raise CartAlreadyCheckedOutException(
                f"Cart id={cartId} is already checked out, cannot remove items"
            )

        item = self._repo.getItemInCart(itemId, cartId)
        if not item:
            raise CartItemNotFoundException(
                f"Item id={itemId} not found in cart id={cartId}"
            )

        self._repo.deleteCartItem(itemId)

    def deleteCart(self, cartId: int):
        cart = self._repo.getCart(cartId)
        if not cart:
            raise CartNotFoundException(f"Cart with id={cartId} not found")

        self._repo.deleteCart(cartId)

    def checkout(self, cartId: int):
        cart = self._repo.getCart(cartId)
        if not cart:
            raise CartNotFoundException(f"Cart with id={cartId} not found")

        if cart["status"] == "checked_out":
            raise CartAlreadyCheckedOutException(
                f"Cart id={cartId} is already checked out"
            )

        if not self._repo.cartHasItems(cartId):
            raise CartEmptyException(
                f"Cart id={cartId} has no items, cannot checkout"
            )

        self._repo.checkoutCart(cartId)
        self._repo.reduceStock(cartId)
        return {"cart_id": cartId, "status": "checked_out"}
