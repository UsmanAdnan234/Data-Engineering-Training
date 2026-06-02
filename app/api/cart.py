from fastapi import APIRouter, HTTPException

from app.schemas.cart import (
    CreateCartRequest,
    CreateCartResponse,
    AddCartItemRequest,
    AddCartItemResponse,
    RemoveCartItemResponse,
    DeleteCartResponse,
    CheckoutResponse,
)

from app.services.cart_service import CartService

from app.database.connection import get_connection

from app.core.logger import logger

from app.core.exceptions import (
    UserNotFoundException,
    CartAlreadyExistsException,
    CartNotFoundException,
    CartAlreadyCheckedOutException,
    CartEmptyException,
    VariantNotFoundException,
    CartItemNotFoundException,
)

router = APIRouter()


@router.post(
    "/carts",
    response_model=CreateCartResponse,
    status_code=201
)
def create_cart(payload: CreateCartRequest):

    conn = get_connection()

    try:

        logger.info(f"Create cart request user_id={payload.user_id}")

        service = CartService(conn)

        result = service.create_cart(payload.user_id)

        logger.info(f"Cart created cart_id={result['cart_id']} user_id={result['user_id']}")

        return {
            "cart_id": result["cart_id"],
            "user_id": result["user_id"],
            "message": "Cart created successfully"
        }

    except UserNotFoundException:

        logger.warning(f"User not found user_id={payload.user_id}")

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    except CartAlreadyExistsException:

        logger.warning(f"Cart already exists for user_id={payload.user_id}")

        raise HTTPException(
            status_code=409,
            detail="Cart already exists for this user"
        )

    except Exception:

        logger.exception("Unexpected error while creating cart user_id=%s", payload.user_id)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        conn.close()


@router.post(
    "/carts/{cart_id}/items",
    response_model=AddCartItemResponse,
    status_code=201
)
def add_item(cart_id: int, payload: AddCartItemRequest):

    conn = get_connection()

    try:

        logger.info(
            f"Add item request cart_id={cart_id} variant_id={payload.variant_id} quantity={payload.quantity}"
        )

        service = CartService(conn)

        result = service.add_item(cart_id, payload.variant_id, payload.quantity)

        logger.info(
            f"Item added item_id={result['item_id']} cart_id={cart_id} variant_id={payload.variant_id} quantity={result['quantity']}"
        )

        return {
            "item_id": result["item_id"],
            "cart_id": result["cart_id"],
            "variant_id": result["variant_id"],
            "quantity": result["quantity"],
            "message": "Item added to cart"
        }

    except CartNotFoundException:

        logger.warning(f"Cart not found cart_id={cart_id}")

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    except CartAlreadyCheckedOutException:

        logger.warning(f"Attempt to modify checked-out cart cart_id={cart_id}")

        raise HTTPException(
            status_code=409,
            detail="Cart is already checked out"
        )

    except VariantNotFoundException:

        logger.warning(f"Variant not found variant_id={payload.variant_id}")

        raise HTTPException(
            status_code=404,
            detail="Product variant not found"
        )

    except Exception:

        logger.exception("Unexpected error while adding item cart_id=%s", cart_id)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        conn.close()


@router.delete(
    "/carts/{cart_id}/items/{item_id}",
    response_model=RemoveCartItemResponse,
    status_code=200
)
def remove_item(cart_id: int, item_id: int):

    conn = get_connection()

    try:

        logger.info(f"Remove item request cart_id={cart_id} item_id={item_id}")

        service = CartService(conn)

        service.remove_item(cart_id, item_id)

        logger.info(f"Item removed item_id={item_id} cart_id={cart_id}")

        return {"message": "Item removed from cart"}

    except CartNotFoundException:

        logger.warning(f"Cart not found cart_id={cart_id}")

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    except CartAlreadyCheckedOutException:

        logger.warning(f"Attempt to modify checked-out cart cart_id={cart_id}")

        raise HTTPException(
            status_code=409,
            detail="Cart is already checked out"
        )

    except CartItemNotFoundException:

        logger.warning(f"Item not found item_id={item_id} cart_id={cart_id}")

        raise HTTPException(
            status_code=404,
            detail="Item not found in cart"
        )

    except Exception:

        logger.exception("Unexpected error while removing item cart_id=%s item_id=%s", cart_id, item_id)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        conn.close()


@router.delete(
    "/carts/{cart_id}",
    response_model=DeleteCartResponse,
    status_code=200
)
def delete_cart(cart_id: int):

    conn = get_connection()

    try:

        logger.info(f"Delete cart request cart_id={cart_id}")

        service = CartService(conn)

        service.delete_cart(cart_id)

        logger.info(f"Cart deleted cart_id={cart_id}")

        return {"message": "Cart deleted successfully"}

    except CartNotFoundException:

        logger.warning(f"Cart not found cart_id={cart_id}")

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    except Exception:

        logger.exception("Unexpected error while deleting cart cart_id=%s", cart_id)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        conn.close()


@router.post(
    "/carts/{cart_id}/checkout",
    response_model=CheckoutResponse,
    status_code=200
)
def checkout(cart_id: int):

    conn = get_connection()

    try:

        logger.info(f"Checkout request cart_id={cart_id}")

        service = CartService(conn)

        result = service.checkout(cart_id)

        logger.info(f"Cart checked out cart_id={cart_id}")

        return {
            "cart_id": result["cart_id"],
            "status": result["status"],
            "message": "Checkout successful"
        }

    except CartNotFoundException:

        logger.warning(f"Cart not found cart_id={cart_id}")

        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    except CartAlreadyCheckedOutException:

        logger.warning(f"Cart already checked out cart_id={cart_id}")

        raise HTTPException(
            status_code=409,
            detail="Cart is already checked out"
        )

    except CartEmptyException:

        logger.warning(f"Checkout attempted on empty cart cart_id={cart_id}")

        raise HTTPException(
            status_code=422,
            detail="Cannot checkout an empty cart"
        )

    except Exception:

        logger.exception("Unexpected error during checkout cart_id=%s", cart_id)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        conn.close()
