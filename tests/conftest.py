import pytest
from unittest.mock import MagicMock

from app.services.cart_service import CartService


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.getUser.return_value = {"user_id": 1, "name": "Asad", "email": "asad@gmail.com"}
    repo.getActiveCartByUser.return_value = None
    repo.createCart.return_value = 1
    repo.getCart.return_value = {"cart_id": 1, "user_id": 1, "status": "active"}
    repo.getVariant.return_value = {"variant_id": 1, "stock": 50, "price": 499.99}
    repo.getCartItem.return_value = None
    repo.addItem.return_value = 1
    repo.getItemInCart.return_value = {"item_id": 1, "cart_id": 1, "variant_id": 1, "quantity": 2}
    repo.cartHasItems.return_value = True
    repo.checkoutCart.return_value = None
    repo.reduceStock.return_value = 1
    repo.deleteCartItem.return_value = None
    repo.deleteCart.return_value = None
    repo.updateQuantity.return_value = None
    return repo


@pytest.fixture
def cart_service(mock_repo):
    return CartService(mock_repo)
