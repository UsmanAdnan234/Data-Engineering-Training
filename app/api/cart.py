from fastapi import APIRouter, HTTPException, Depends

from app.schemas.cart import (
    CreateCartRequest,
    CreateCartResponse,
    AddCartItemRequest,
    AddCartItemResponse,
    RemoveCartItemResponse,
    DeleteCartResponse,
    CheckoutResponse,
)
from app.services.cart_service import ICartService, CartService
from app.repositories.cart_repository import CartRepository
from app.database.connection import DatabaseConnection
from app.core.logger import logger
from app.core.exceptions import (
    UserNotFoundException,
    CartAlreadyExistsException,
    CartNotFoundException,
    CartAlreadyCheckedOutException,
    CartEmptyException,
    VariantNotFoundException,
    CartItemNotFoundException,
    DatabaseException,
)

router = APIRouter()


def getCartService() -> ICartService:
    conn = DatabaseConnection.getInstance()
    return CartService(CartRepository(conn))


def _err(statusCode: int, code: str, message: str):
    raise HTTPException(
        status_code=statusCode,
        detail={"error": code, "message": message}
    )


@router.post("/carts", response_model=CreateCartResponse, status_code=201)
def createCart(
    payload: CreateCartRequest,
    service: ICartService = Depends(getCartService)
):
    logger.info(f"[createCart] Request received | user_id={payload.user_id}")

    try:
        result = service.createCart(payload.user_id)

        logger.info(
            f"[createCart] Cart created | cart_id={result['cart_id']} user_id={result['user_id']}"
        )

        return {
            "cart_id": result["cart_id"],
            "user_id": result["user_id"],
            "message": "Cart created successfully"
        }

    except UserNotFoundException as e:
        logger.warning(f"[createCart] User not found | user_id={payload.user_id} | cause: {e}")
        _err(404, "USER_NOT_FOUND", f"User with id={payload.user_id} not found")

    except CartAlreadyExistsException as e:
        logger.warning(f"[createCart] Active cart already exists | user_id={payload.user_id} | cause: {e}")
        _err(409, "CART_ALREADY_EXISTS", "An active cart already exists for this user")

    except DatabaseException as e:
        logger.error(f"[createCart] Database error | user_id={payload.user_id} | cause: {e}")
        _err(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable, please try again")

    except Exception as e:
        logger.exception(f"[createCart] Unexpected error | user_id={payload.user_id} | cause: {e}")
        _err(500, "INTERNAL_ERROR", "An unexpected error occurred")


@router.post("/carts/{cart_id}/items", response_model=AddCartItemResponse, status_code=201)
def addItem(
    cart_id: int,
    payload: AddCartItemRequest,
    service: ICartService = Depends(getCartService)
):
    logger.info(
        f"[addItem] Request received | cart_id={cart_id} variant_id={payload.variant_id} quantity={payload.quantity}"
    )

    try:
        result = service.addItem(cart_id, payload.variant_id, payload.quantity)

        logger.info(
            f"[addItem] Item added | item_id={result['item_id']} cart_id={cart_id} "
            f"variant_id={result['variant_id']} quantity={result['quantity']}"
        )

        return {
            "item_id": result["item_id"],
            "cart_id": result["cart_id"],
            "variant_id": result["variant_id"],
            "quantity": result["quantity"],
            "message": "Item added to cart"
        }

    except CartNotFoundException as e:
        logger.warning(f"[addItem] Cart not found | cart_id={cart_id} | cause: {e}")
        _err(404, "CART_NOT_FOUND", f"Cart with id={cart_id} not found")

    except CartAlreadyCheckedOutException as e:
        logger.warning(f"[addItem] Cart is checked out | cart_id={cart_id} | cause: {e}")
        _err(409, "CART_CHECKED_OUT", f"Cart with id={cart_id} is already checked out")

    except VariantNotFoundException as e:
        logger.warning(
            f"[addItem] Variant not found | variant_id={payload.variant_id} cart_id={cart_id} | cause: {e}"
        )
        _err(404, "VARIANT_NOT_FOUND", f"Product variant with id={payload.variant_id} not found")

    except DatabaseException as e:
        logger.error(f"[addItem] Database error | cart_id={cart_id} | cause: {e}")
        _err(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable, please try again")

    except Exception as e:
        logger.exception(f"[addItem] Unexpected error | cart_id={cart_id} | cause: {e}")
        _err(500, "INTERNAL_ERROR", "An unexpected error occurred")


@router.delete(
    "/carts/{cart_id}/items/{item_id}",
    response_model=RemoveCartItemResponse,
    status_code=200
)
def removeItem(
    cart_id: int,
    item_id: int,
    service: ICartService = Depends(getCartService)
):
    logger.info(f"[removeItem] Request received | cart_id={cart_id} item_id={item_id}")

    try:
        service.removeItem(cart_id, item_id)

        logger.info(f"[removeItem] Item removed | item_id={item_id} cart_id={cart_id}")

        return {"message": "Item removed from cart"}

    except CartNotFoundException as e:
        logger.warning(f"[removeItem] Cart not found | cart_id={cart_id} | cause: {e}")
        _err(404, "CART_NOT_FOUND", f"Cart with id={cart_id} not found")

    except CartAlreadyCheckedOutException as e:
        logger.warning(f"[removeItem] Cart is checked out | cart_id={cart_id} | cause: {e}")
        _err(409, "CART_CHECKED_OUT", f"Cart with id={cart_id} is already checked out")

    except CartItemNotFoundException as e:
        logger.warning(
            f"[removeItem] Item not found | item_id={item_id} cart_id={cart_id} | cause: {e}"
        )
        _err(404, "ITEM_NOT_FOUND", f"Item with id={item_id} not found in cart {cart_id}")

    except DatabaseException as e:
        logger.error(f"[removeItem] Database error | cart_id={cart_id} item_id={item_id} | cause: {e}")
        _err(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable, please try again")

    except Exception as e:
        logger.exception(
            f"[removeItem] Unexpected error | cart_id={cart_id} item_id={item_id} | cause: {e}"
        )
        _err(500, "INTERNAL_ERROR", "An unexpected error occurred")


@router.delete("/carts/{cart_id}", response_model=DeleteCartResponse, status_code=200)
def deleteCart(
    cart_id: int,
    service: ICartService = Depends(getCartService)
):
    logger.info(f"[deleteCart] Request received | cart_id={cart_id}")

    try:
        service.deleteCart(cart_id)

        logger.info(f"[deleteCart] Cart deleted | cart_id={cart_id}")

        return {"message": "Cart deleted successfully"}

    except CartNotFoundException as e:
        logger.warning(f"[deleteCart] Cart not found | cart_id={cart_id} | cause: {e}")
        _err(404, "CART_NOT_FOUND", f"Cart with id={cart_id} not found")

    except DatabaseException as e:
        logger.error(f"[deleteCart] Database error | cart_id={cart_id} | cause: {e}")
        _err(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable, please try again")

    except Exception as e:
        logger.exception(f"[deleteCart] Unexpected error | cart_id={cart_id} | cause: {e}")
        _err(500, "INTERNAL_ERROR", "An unexpected error occurred")


@router.post("/carts/{cart_id}/checkout", response_model=CheckoutResponse, status_code=200)
def checkout(
    cart_id: int,
    service: ICartService = Depends(getCartService)
):
    logger.info(f"[checkout] Request received | cart_id={cart_id}")

    try:
        result = service.checkout(cart_id)

        logger.info(f"[checkout] Cart checked out | cart_id={cart_id}")

        return {
            "cart_id": result["cart_id"],
            "status": result["status"],
            "message": "Checkout successful"
        }

    except CartNotFoundException as e:
        logger.warning(f"[checkout] Cart not found | cart_id={cart_id} | cause: {e}")
        _err(404, "CART_NOT_FOUND", f"Cart with id={cart_id} not found")

    except CartAlreadyCheckedOutException as e:
        logger.warning(f"[checkout] Cart already checked out | cart_id={cart_id} | cause: {e}")
        _err(409, "CART_CHECKED_OUT", f"Cart with id={cart_id} is already checked out")

    except CartEmptyException as e:
        logger.warning(f"[checkout] Cart is empty | cart_id={cart_id} | cause: {e}")
        _err(422, "CART_EMPTY", f"Cart with id={cart_id} has no items, cannot checkout")

    except DatabaseException as e:
        logger.error(f"[checkout] Database error | cart_id={cart_id} | cause: {e}")
        _err(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable, please try again")

    except Exception as e:
        logger.exception(f"[checkout] Unexpected error | cart_id={cart_id} | cause: {e}")
        _err(500, "INTERNAL_ERROR", "An unexpected error occurred")
