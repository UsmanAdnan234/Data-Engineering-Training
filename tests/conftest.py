from unittest.mock import MagicMock

import psycopg2
import pytest

from app.services.cart_service import CartService


@pytest.fixture(scope="session")
def seeded_db():
    """Reset and seed the database once per test session for integration tests.
    Skips gracefully if the database is not reachable (e.g. no docker-compose up).
    """
    try:
        from app.core.config import DATABASE_URL
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            TRUNCATE cart_items, carts, product_variants, products, users
            RESTART IDENTITY CASCADE
        """)
        cur.executemany(
            "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)",
            [
                ("Asad",     "asad@gmail.com",     "03345678910"),
                ("Muzammil", "muzammil@gmail.com", "03001234588"),
                ("Zainab",   "zainab@gmail.com",   "03005556677"),
                ("Ali",      "ali@gmail.com",      "03112223344"),
                ("Sara",     "sara@gmail.com",     "03223334455"),
            ],
        )
        cur.executemany(
            "INSERT INTO products (name) VALUES (%s)",
            [("T-Shirt",), ("Jeans",), ("Sneakers",), ("Hoodie",), ("Cap",)],
        )
        cur.executemany(
            "INSERT INTO product_variants (product_id, color, size, price, stock) VALUES (%s,%s,%s,%s,%s)",
            [
                (1, "White", "S",    499.99,  50),  # variant 1  — stock=50
                (1, "Black", "M",    499.99,  30),  # variant 2  — stock=30
                (1, "Red",   "L",    549.99,  20),  # variant 3  — stock=20
                (2, "Blue",  "30",  1999.00,  15),  # variant 4  — stock=15
                (2, "Black", "32",  2199.00,  10),  # variant 5  — stock=10 (TC-19a/b)
                (3, "White", "42",  3499.00,   8),  # variant 6  — stock=8  (TC-18)
                (3, "Black", "43",  3499.00,   5),  # variant 7  — stock=5  (TC-14,41,42,50)
                (4, "Gray",  "S",   1499.00,  25),  # variant 8
                (4, "Black", "M",   1599.00,  20),  # variant 9
                (4, "Navy",  "L",   1599.00,  15),  # variant 10
                (5, "Black", "Free",  299.00, 100),  # variant 11
                (5, "White", "Free",  299.00,  80),  # variant 12
                (5, "Red",   "Free",  349.00,  60),  # variant 13
            ],
        )
        conn.commit()
        conn.close()
    except Exception as e:
        pytest.skip(f"Database not reachable — skipping integration tests. Run docker-compose up first. ({e})")
    yield


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
