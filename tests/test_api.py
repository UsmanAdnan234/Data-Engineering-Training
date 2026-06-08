"""
Integration tests — all 50 TC-xx test cases from the Postman collection,
plus setup helpers, converted to pytest using FastAPI's TestClient.

Tests run against a real PostgreSQL database (seeded by the `seeded_db`
fixture in conftest.py). They are stateful and must run in definition order
— each group builds on state created by the previous one.

Local prerequisites:
    docker-compose up -d
    alembic upgrade head
    pytest tests/test_api.py -v

In CI the database is provided by the postgres service container and seeded
automatically before this file runs.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.usefixtures("seeded_db")

client = TestClient(app)

# Shared state — IDs created during tests, used by later tests
S: dict = {}


# =============================================================================
# GROUP A — Create Cart (TC-01 – TC-10)
# =============================================================================

class TestGroupA_CreateCart:

    def test_tc01_create_cart_user1(self):
        r = client.post("/carts", json={"user_id": 1})
        assert r.status_code == 201
        data = r.json()
        assert data["user_id"] == 1
        assert data["message"] == "Cart created successfully"
        S["cart1"] = data["cart_id"]

    def test_tc02_create_cart_user2(self):
        r = client.post("/carts", json={"user_id": 2})
        assert r.status_code == 201
        data = r.json()
        assert data["user_id"] == 2
        S["cart2"] = data["cart_id"]

    def test_tc03_duplicate_cart(self):
        r = client.post("/carts", json={"user_id": 1})
        assert r.status_code == 409
        assert r.json()["error"] == "CART_ALREADY_EXISTS"

    def test_tc04_nonexistent_user(self):
        r = client.post("/carts", json={"user_id": 999})
        assert r.status_code == 404
        assert r.json()["error"] == "USER_NOT_FOUND"

    def test_tc05_user_id_zero(self):
        r = client.post("/carts", json={"user_id": 0})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc06_user_id_negative(self):
        r = client.post("/carts", json={"user_id": -1})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc07_user_id_string(self):
        r = client.post("/carts", json={"user_id": "abc"})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc08_user_id_missing(self):
        r = client.post("/carts", json={})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc09_user_id_overflow(self):
        r = client.post("/carts", json={"user_id": 99999999999999999999})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc10_user_id_decimal(self):
        r = client.post("/carts", json={"user_id": 1.5})
        assert r.status_code == 422
        data = r.json()
        assert data["error"] == "VALIDATION_ERROR"
        assert any("no decimal" in d["message"].lower() for d in data["details"])


# =============================================================================
# GROUP B — Add Item (TC-11 – TC-25)
# =============================================================================

class TestGroupB_AddItem:

    def test_tc11_add_new_item(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 1, "quantity": 2})
        assert r.status_code == 201
        data = r.json()
        assert data["variant_id"] == 1
        assert data["quantity"] == 2
        assert data["message"] == "Item added to cart"
        S["item_v1"] = data["item_id"]

    def test_tc12_same_variant_accumulates(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 1, "quantity": 1})
        assert r.status_code == 201
        data = r.json()
        assert data["quantity"] == 3          # 2 + 1 accumulated
        assert data["item_id"] == S["item_v1"]  # same item updated, not a new one

    def test_tc13_add_different_variant(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 4, "quantity": 2})
        assert r.status_code == 201
        data = r.json()
        assert data["variant_id"] == 4
        S["item_v4"] = data["item_id"]

    def test_tc14_add_exact_stock(self):
        # variant 7 has stock=5; adding exactly 5 must succeed
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 7, "quantity": 5})
        assert r.status_code == 201
        data = r.json()
        assert data["quantity"] == 5
        S["item_v7"] = data["item_id"]

    def test_tc15_add_to_nonexistent_cart(self):
        r = client.post("/carts/9999/items", json={"variant_id": 1, "quantity": 1})
        assert r.status_code == 404
        assert r.json()["error"] == "CART_NOT_FOUND"

    def test_tc16_nonexistent_variant(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 9999, "quantity": 1})
        assert r.status_code == 404
        assert r.json()["error"] == "VARIANT_NOT_FOUND"

    # ── Setup for TC-17: create cart user3, add item, checkout ──────────────
    def test_setup_tc17_checkout_user3_cart(self):
        r = client.post("/carts", json={"user_id": 3})
        assert r.status_code == 201
        S["cart3"] = r.json()["cart_id"]

        r = client.post(f"/carts/{S['cart3']}/items", json={"variant_id": 2, "quantity": 1})
        assert r.status_code == 201
        S["item_cart3"] = r.json()["item_id"]

        r = client.post(f"/carts/{S['cart3']}/checkout")
        assert r.status_code == 200

    def test_tc17_add_to_checked_out_cart(self):
        r = client.post(f"/carts/{S['cart3']}/items", json={"variant_id": 1, "quantity": 1})
        assert r.status_code == 409
        assert r.json()["error"] == "CART_CHECKED_OUT"

    def test_tc18_quantity_exceeds_stock(self):
        # variant 6 has stock=8; requesting 10 must fail
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 6, "quantity": 10})
        assert r.status_code == 422
        assert r.json()["error"] == "INSUFFICIENT_STOCK"

    def test_tc19a_add_partial_stock(self):
        # variant 5 stock=10; add 7 (still under limit)
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 5, "quantity": 7})
        assert r.status_code == 201
        data = r.json()
        assert data["quantity"] == 7
        S["item_v5"] = data["item_id"]

    def test_tc19b_accumulated_exceeds_stock(self):
        # variant 5 already has qty=7 in cart; adding 5 more = 12 > stock 10
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 5, "quantity": 5})
        assert r.status_code == 422
        assert r.json()["error"] == "INSUFFICIENT_STOCK"

    def test_tc20_quantity_zero(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 1, "quantity": 0})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc21_quantity_negative(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 1, "quantity": -1})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc22_variant_id_zero(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 0, "quantity": 1})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc23_variant_id_negative(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": -1, "quantity": 1})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc24_variant_id_missing(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"quantity": 1})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc25_quantity_missing(self):
        r = client.post(f"/carts/{S['cart1']}/items", json={"variant_id": 1})
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"


# =============================================================================
# GROUP C — Remove Item (TC-26 – TC-33)
# =============================================================================

class TestGroupC_RemoveItem:

    def test_tc26_remove_existing_item(self):
        # Remove variant 4 item from cart1
        r = client.delete(f"/carts/{S['cart1']}/items/{S['item_v4']}")
        assert r.status_code == 200
        assert r.json()["message"] == "Item removed from cart"

    def test_tc27_remove_from_nonexistent_cart(self):
        r = client.delete(f"/carts/9999/items/{S['item_v1']}")
        assert r.status_code == 404
        assert r.json()["error"] == "CART_NOT_FOUND"

    def test_tc28_remove_nonexistent_item(self):
        r = client.delete(f"/carts/{S['cart1']}/items/9999")
        assert r.status_code == 404
        assert r.json()["error"] == "ITEM_NOT_FOUND"

    def test_tc29_remove_item_from_wrong_cart(self):
        # item_v1 belongs to cart1 — trying to remove it via cart2 must fail
        r = client.delete(f"/carts/{S['cart2']}/items/{S['item_v1']}")
        assert r.status_code == 404
        assert r.json()["error"] == "ITEM_NOT_FOUND"

    def test_tc30_remove_from_checked_out_cart(self):
        # cart3 is checked out — any removal attempt must return 409
        r = client.delete(f"/carts/{S['cart3']}/items/{S['item_cart3']}")
        assert r.status_code == 409
        assert r.json()["error"] == "CART_CHECKED_OUT"

    def test_tc31_cart_id_zero(self):
        r = client.delete("/carts/0/items/1")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc32_item_id_zero(self):
        r = client.delete(f"/carts/{S['cart1']}/items/0")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc33_cart_id_overflow(self):
        r = client.delete("/carts/99999999999999999999/items/1")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"


# =============================================================================
# GROUP D — Delete Cart (TC-34 – TC-40)
# =============================================================================

class TestGroupD_DeleteCart:

    def test_tc34_delete_active_cart(self):
        # cart2 is active and empty — delete it
        r = client.delete(f"/carts/{S['cart2']}")
        assert r.status_code == 200
        assert r.json()["message"] == "Cart deleted successfully"

    # ── Setup for TC-35: recreate cart2 with an item ─────────────────────────
    def test_setup_tc35_create_cart_with_items(self):
        r = client.post("/carts", json={"user_id": 2})
        assert r.status_code == 201
        S["cart2_new"] = r.json()["cart_id"]

        r = client.post(f"/carts/{S['cart2_new']}/items", json={"variant_id": 3, "quantity": 1})
        assert r.status_code == 201

    def test_tc35_delete_cart_cascades_items(self):
        r = client.delete(f"/carts/{S['cart2_new']}")
        assert r.status_code == 200
        # Verify cart (and its items via CASCADE) is gone
        r2 = client.delete(f"/carts/{S['cart2_new']}")
        assert r2.status_code == 404
        assert r2.json()["error"] == "CART_NOT_FOUND"

    def test_tc36_delete_nonexistent_cart(self):
        r = client.delete("/carts/9999")
        assert r.status_code == 404
        assert r.json()["error"] == "CART_NOT_FOUND"

    def test_tc37_cart_id_zero(self):
        r = client.delete("/carts/0")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc38_cart_id_negative(self):
        r = client.delete("/carts/-1")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc39_cart_id_overflow(self):
        r = client.delete("/carts/99999999999999999999")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc40_delete_checked_out_cart(self):
        # Service allows deleting a checked-out cart (no status guard on deleteCart)
        r = client.delete(f"/carts/{S['cart3']}")
        assert r.status_code == 200
        assert r.json()["message"] == "Cart deleted successfully"


# =============================================================================
# GROUP E — Checkout (TC-41 – TC-47)
# =============================================================================

class TestGroupE_Checkout:

    def test_tc41_checkout_active_cart(self):
        # cart1 contains: v1(qty=3), v7(qty=5), v5(qty=7)
        # After checkout: v1 stock 50→47, v7 stock 5→0, v5 stock 10→3
        r = client.post(f"/carts/{S['cart1']}/checkout")
        assert r.status_code == 200
        data = r.json()
        assert data["cart_id"] == S["cart1"]
        assert data["status"] == "checked_out"
        assert data["message"] == "Checkout successful"

    # ── Setup for TC-42: new cart for user1 (old cart just checked out) ──────
    def test_setup_tc42_new_cart_user1(self):
        r = client.post("/carts", json={"user_id": 1})
        assert r.status_code == 201
        S["cart1_new"] = r.json()["cart_id"]

    def test_tc42_stock_reduced_after_checkout(self):
        # variant 7 stock is now 0 — any quantity must fail
        r = client.post(f"/carts/{S['cart1_new']}/items", json={"variant_id": 7, "quantity": 1})
        assert r.status_code == 422
        assert r.json()["error"] == "INSUFFICIENT_STOCK"

    def test_tc43_checkout_nonexistent_cart(self):
        r = client.post("/carts/9999/checkout")
        assert r.status_code == 404
        assert r.json()["error"] == "CART_NOT_FOUND"

    def test_tc44_checkout_already_checked_out(self):
        r = client.post(f"/carts/{S['cart1']}/checkout")
        assert r.status_code == 409
        assert r.json()["error"] == "CART_CHECKED_OUT"

    # ── Setup for TC-45: empty cart for user2 ───────────────────────────────
    def test_setup_tc45_empty_cart_user2(self):
        r = client.post("/carts", json={"user_id": 2})
        assert r.status_code == 201
        S["cart2_empty"] = r.json()["cart_id"]

    def test_tc45_checkout_empty_cart(self):
        r = client.post(f"/carts/{S['cart2_empty']}/checkout")
        assert r.status_code == 422
        assert r.json()["error"] == "CART_EMPTY"

    def test_tc46_cart_id_zero(self):
        r = client.post("/carts/0/checkout")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"

    def test_tc47_cart_id_overflow(self):
        r = client.post("/carts/99999999999999999999/checkout")
        assert r.status_code == 422
        assert r.json()["error"] == "VALIDATION_ERROR"


# =============================================================================
# GROUP F — Lifecycle (TC-48 – TC-50)
# =============================================================================

class TestGroupF_Lifecycle:

    def test_tc48_complete_happy_path(self):
        # Create cart for user 4
        r = client.post("/carts", json={"user_id": 4})
        assert r.status_code == 201
        S["cart4"] = r.json()["cart_id"]

        # Add variant 1 (stock=47 after TC-41) qty=5
        r = client.post(f"/carts/{S['cart4']}/items", json={"variant_id": 1, "quantity": 5})
        assert r.status_code == 201
        assert r.json()["quantity"] == 5

        # Add variant 4 (stock=15) qty=3
        r = client.post(f"/carts/{S['cart4']}/items", json={"variant_id": 4, "quantity": 3})
        assert r.status_code == 201
        assert r.json()["quantity"] == 3

        # Checkout
        r = client.post(f"/carts/{S['cart4']}/checkout")
        assert r.status_code == 200
        assert r.json()["status"] == "checked_out"
        assert r.json()["cart_id"] == S["cart4"]

    def test_tc49_new_cart_after_checkout(self):
        # cart4 is checked out — user 4 can create a fresh cart
        r = client.post("/carts", json={"user_id": 4})
        assert r.status_code == 201
        data = r.json()
        assert data["user_id"] == 4
        S["cart4_new"] = data["cart_id"]

    def test_tc50_variant7_out_of_stock(self):
        # variant 7 stock = 0 since TC-41 checkout — must still be blocked
        r = client.post(f"/carts/{S['cart4_new']}/items", json={"variant_id": 7, "quantity": 1})
        assert r.status_code == 422
        assert r.json()["error"] == "INSUFFICIENT_STOCK"
