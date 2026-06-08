import pytest
from unittest.mock import MagicMock

from app.core.exceptions import (
    CartAlreadyCheckedOutException,
    CartAlreadyExistsException,
    CartEmptyException,
    CartItemNotFoundException,
    CartNotFoundException,
    InsufficientStockException,
    UserNotFoundException,
    VariantNotFoundException,
)
from app.services.cart_service import CartService


# ─────────────────────────────────────────
# createCart
# ─────────────────────────────────────────

class TestCreateCart:

    def test_create_cart_success(self, cart_service, mock_repo):
        result = cart_service.createCart(1)
        assert result["cart_id"] == 1
        assert result["user_id"] == 1
        mock_repo.createCart.assert_called_once_with(1)

    def test_create_cart_user_not_found(self, cart_service, mock_repo):
        mock_repo.getUser.return_value = None
        with pytest.raises(UserNotFoundException):
            cart_service.createCart(999)

    def test_create_cart_already_exists(self, cart_service, mock_repo):
        mock_repo.getActiveCartByUser.return_value = {"cart_id": 5, "user_id": 1, "status": "active"}
        with pytest.raises(CartAlreadyExistsException):
            cart_service.createCart(1)

    def test_create_cart_does_not_call_create_if_user_not_found(self, cart_service, mock_repo):
        mock_repo.getUser.return_value = None
        with pytest.raises(UserNotFoundException):
            cart_service.createCart(999)
        mock_repo.createCart.assert_not_called()

    def test_create_cart_returns_correct_user_id(self, cart_service, mock_repo):
        mock_repo.createCart.return_value = 42
        result = cart_service.createCart(1)
        assert result["cart_id"] == 42
        assert result["user_id"] == 1


# ─────────────────────────────────────────
# addItem
# ─────────────────────────────────────────

class TestAddItem:

    def test_add_new_item_success(self, cart_service, mock_repo):
        mock_repo.addItem.return_value = 10
        result = cart_service.addItem(1, 1, 2)
        assert result["item_id"] == 10
        assert result["cart_id"] == 1
        assert result["variant_id"] == 1
        assert result["quantity"] == 2

    def test_add_item_cart_not_found(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = None
        with pytest.raises(CartNotFoundException):
            cart_service.addItem(9999, 1, 1)

    def test_add_item_cart_already_checked_out(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = {"cart_id": 1, "user_id": 1, "status": "checked_out"}
        with pytest.raises(CartAlreadyCheckedOutException):
            cart_service.addItem(1, 1, 1)

    def test_add_item_variant_not_found(self, cart_service, mock_repo):
        mock_repo.getVariant.return_value = None
        with pytest.raises(VariantNotFoundException):
            cart_service.addItem(1, 9999, 1)

    def test_add_item_insufficient_stock(self, cart_service, mock_repo):
        mock_repo.getVariant.return_value = {"variant_id": 1, "stock": 5, "price": 499.99}
        with pytest.raises(InsufficientStockException):
            cart_service.addItem(1, 1, 10)

    def test_add_item_exact_stock_passes(self, cart_service, mock_repo):
        mock_repo.getVariant.return_value = {"variant_id": 1, "stock": 5, "price": 499.99}
        mock_repo.addItem.return_value = 1
        result = cart_service.addItem(1, 1, 5)
        assert result["quantity"] == 5

    def test_add_same_variant_accumulates_quantity(self, cart_service, mock_repo):
        mock_repo.getCartItem.return_value = {"item_id": 1, "cart_id": 1, "variant_id": 1, "quantity": 3}
        mock_repo.getVariant.return_value = {"variant_id": 1, "stock": 50, "price": 499.99}
        result = cart_service.addItem(1, 1, 2)
        assert result["quantity"] == 5
        assert result["item_id"] == 1
        mock_repo.updateQuantity.assert_called_once_with(1, 5)

    def test_add_same_variant_accumulated_exceeds_stock(self, cart_service, mock_repo):
        mock_repo.getCartItem.return_value = {"item_id": 1, "cart_id": 1, "variant_id": 1, "quantity": 8}
        mock_repo.getVariant.return_value = {"variant_id": 1, "stock": 10, "price": 499.99}
        with pytest.raises(InsufficientStockException):
            cart_service.addItem(1, 1, 5)

    def test_add_item_does_not_insert_duplicate(self, cart_service, mock_repo):
        mock_repo.getCartItem.return_value = {"item_id": 1, "cart_id": 1, "variant_id": 1, "quantity": 2}
        mock_repo.getVariant.return_value = {"variant_id": 1, "stock": 50, "price": 499.99}
        cart_service.addItem(1, 1, 3)
        mock_repo.addItem.assert_not_called()


# ─────────────────────────────────────────
# removeItem
# ─────────────────────────────────────────

class TestRemoveItem:

    def test_remove_item_success(self, cart_service, mock_repo):
        cart_service.removeItem(1, 1)
        mock_repo.deleteCartItem.assert_called_once_with(1)

    def test_remove_item_cart_not_found(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = None
        with pytest.raises(CartNotFoundException):
            cart_service.removeItem(9999, 1)

    def test_remove_item_cart_checked_out(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = {"cart_id": 1, "user_id": 1, "status": "checked_out"}
        with pytest.raises(CartAlreadyCheckedOutException):
            cart_service.removeItem(1, 1)

    def test_remove_item_not_found_in_cart(self, cart_service, mock_repo):
        mock_repo.getItemInCart.return_value = None
        with pytest.raises(CartItemNotFoundException):
            cart_service.removeItem(1, 9999)

    def test_remove_item_does_not_delete_if_cart_checked_out(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = {"cart_id": 1, "user_id": 1, "status": "checked_out"}
        with pytest.raises(CartAlreadyCheckedOutException):
            cart_service.removeItem(1, 1)
        mock_repo.deleteCartItem.assert_not_called()


# ─────────────────────────────────────────
# deleteCart
# ─────────────────────────────────────────

class TestDeleteCart:

    def test_delete_cart_success(self, cart_service, mock_repo):
        cart_service.deleteCart(1)
        mock_repo.deleteCart.assert_called_once_with(1)

    def test_delete_cart_not_found(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = None
        with pytest.raises(CartNotFoundException):
            cart_service.deleteCart(9999)

    def test_delete_cart_does_not_delete_if_not_found(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = None
        with pytest.raises(CartNotFoundException):
            cart_service.deleteCart(9999)
        mock_repo.deleteCart.assert_not_called()


# ─────────────────────────────────────────
# checkout
# ─────────────────────────────────────────

class TestCheckout:

    def test_checkout_success(self, cart_service, mock_repo):
        result = cart_service.checkout(1)
        assert result["cart_id"] == 1
        assert result["status"] == "checked_out"
        mock_repo.checkoutCart.assert_called_once_with(1)
        mock_repo.reduceStock.assert_called_once_with(1)

    def test_checkout_cart_not_found(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = None
        with pytest.raises(CartNotFoundException):
            cart_service.checkout(9999)

    def test_checkout_already_checked_out(self, cart_service, mock_repo):
        mock_repo.getCart.return_value = {"cart_id": 1, "user_id": 1, "status": "checked_out"}
        with pytest.raises(CartAlreadyCheckedOutException):
            cart_service.checkout(1)

    def test_checkout_empty_cart(self, cart_service, mock_repo):
        mock_repo.cartHasItems.return_value = False
        with pytest.raises(CartEmptyException):
            cart_service.checkout(1)

    def test_checkout_reduces_stock(self, cart_service, mock_repo):
        cart_service.checkout(1)
        mock_repo.reduceStock.assert_called_once_with(1)

    def test_checkout_does_not_reduce_stock_if_empty(self, cart_service, mock_repo):
        mock_repo.cartHasItems.return_value = False
        with pytest.raises(CartEmptyException):
            cart_service.checkout(1)
        mock_repo.reduceStock.assert_not_called()
