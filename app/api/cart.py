from typing import Annotated, Generator

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.exceptions import (
    CartAlreadyCheckedOutException,
    CartAlreadyExistsException,
    CartEmptyException,
    CartItemNotFoundException,
    CartNotFoundException,
    DatabaseException,
    InsufficientStockException,
    UserNotFoundException,
    VariantNotFoundException,
)
from app.core.logger import logger
from app.database.connection import DatabaseConnection
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import (
    AddCartItemRequest,
    AddCartItemResponse,
    CheckoutResponse,
    CreateCartRequest,
    CreateCartResponse,
    DeleteCartResponse,
    RemoveCartItemResponse,
)
from app.services.cart_service import CartService, ICartService

router = APIRouter()

SQLITE_INT_MAX = 9223372036854775807


def get_db() -> Generator:
    conn = DatabaseConnection.getconn()
    try:
        yield conn
    finally:
        DatabaseConnection.putconn(conn)


def getCartService(conn=Depends(get_db)) -> ICartService:
    return CartService(CartRepository(conn))


def _err(statusCode: int, code: str, message: str):
    raise HTTPException(
        status_code=statusCode,
        detail={"error": code, "message": message}
    )


# =========================
# CREATE CART
# =========================
@router.post("/carts", response_model=CreateCartResponse, status_code=201)
def createCart(payload: CreateCartRequest, service: ICartService = Depends(getCartService)):

    logger.info(f"[createCart] | event=request_received | user_id={payload.user_id}")

    try:
        result = service.createCart(payload.user_id)

        logger.info(
            f"[createCart] | status_code=201 | event=cart_created"
            f" | cart_id={result['cart_id']} | user_id={result['user_id']}"
        )

        return {
            "cart_id": result["cart_id"],
            "user_id": result["user_id"],
            "message": "Cart created successfully"
        }

    except UserNotFoundException as e:
        logger.warning(
            f"[createCart] | status_code=404 | error=USER_NOT_FOUND"
            f" | user_id={payload.user_id} | cause={e}"
        )
        _err(404, "USER_NOT_FOUND", "User not found")

    except CartAlreadyExistsException as e:
        logger.warning(
            f"[createCart] | status_code=409 | error=CART_ALREADY_EXISTS"
            f" | user_id={payload.user_id} | cause={e}"
        )
        _err(409, "CART_ALREADY_EXISTS", "Active cart already exists")

    except DatabaseException as e:
        logger.error(
            f"[createCart] | status_code=503 | error=DATABASE_ERROR"
            f" | user_id={payload.user_id} | cause={e}"
        )
        _err(503, "SERVICE_UNAVAILABLE", "Service temporarily unavailable")

    except Exception:
        logger.exception(
            f"[createCart] | status_code=500 | error=INTERNAL_ERROR | user_id={payload.user_id}"
        )
        _err(500, "INTERNAL_ERROR", "Unexpected error")


# =========================
# ADD ITEM
# =========================
@router.post("/carts/{cart_id}/items", response_model=AddCartItemResponse, status_code=201)
def addItem(
    cart_id: Annotated[int, Path(gt=0, le=SQLITE_INT_MAX)],
    payload: AddCartItemRequest,
    service: ICartService = Depends(getCartService)
):

    logger.info(
        f"[addItem] | event=request_received"
        f" | cart_id={cart_id} | variant_id={payload.variant_id} | quantity={payload.quantity}"
    )

    try:
        result = service.addItem(cart_id, payload.variant_id, payload.quantity)

        logger.info(
            f"[addItem] | status_code=201 | event=item_added"
            f" | cart_id={cart_id} | item_id={result['item_id']} | quantity={result['quantity']}"
        )

        return {
            "item_id": result["item_id"],
            "cart_id": result["cart_id"],
            "variant_id": result["variant_id"],
            "quantity": result["quantity"],
            "message": "Item added to cart"
        }

    except CartNotFoundException as e:
        logger.warning(
            f"[addItem] | status_code=404 | error=CART_NOT_FOUND | cart_id={cart_id} | cause={e}"
        )
        _err(404, "CART_NOT_FOUND", "Cart not found")

    except CartAlreadyCheckedOutException as e:
        logger.warning(
            f"[addItem] | status_code=409 | error=CART_CHECKED_OUT | cart_id={cart_id} | cause={e}"
        )
        _err(409, "CART_CHECKED_OUT", "Cart already checked out")

    except VariantNotFoundException as e:
        logger.warning(
            f"[addItem] | status_code=404 | error=VARIANT_NOT_FOUND"
            f" | cart_id={cart_id} | variant_id={payload.variant_id} | cause={e}"
        )
        _err(404, "VARIANT_NOT_FOUND", "Variant not found")

    except InsufficientStockException as e:
        logger.warning(
            f"[addItem] | status_code=422 | error=INSUFFICIENT_STOCK"
            f" | cart_id={cart_id} | variant_id={payload.variant_id} | quantity={payload.quantity} | cause={e}"
        )
        _err(422, "INSUFFICIENT_STOCK", "Requested quantity exceeds available stock")

    except DatabaseException as e:
        logger.error(
            f"[addItem] | status_code=503 | error=DATABASE_ERROR | cart_id={cart_id} | cause={e}"
        )
        _err(503, "SERVICE_UNAVAILABLE", "Service unavailable")

    except Exception:
        logger.exception(
            f"[addItem] | status_code=500 | error=INTERNAL_ERROR | cart_id={cart_id}"
        )
        _err(500, "INTERNAL_ERROR", "Unexpected error")


# =========================
# REMOVE ITEM
# =========================
@router.delete("/carts/{cart_id}/items/{item_id}", response_model=RemoveCartItemResponse, status_code=200)
def removeItem(
    cart_id: Annotated[int, Path(gt=0, le=SQLITE_INT_MAX)],
    item_id: Annotated[int, Path(gt=0, le=SQLITE_INT_MAX)],
    service: ICartService = Depends(getCartService)
):

    logger.info(
        f"[removeItem] | event=request_received | cart_id={cart_id} | item_id={item_id}"
    )

    try:
        service.removeItem(cart_id, item_id)

        logger.info(
            f"[removeItem] | status_code=200 | event=item_removed | cart_id={cart_id} | item_id={item_id}"
        )

        return {"message": "Item removed from cart"}

    except CartNotFoundException as e:
        logger.warning(
            f"[removeItem] | status_code=404 | error=CART_NOT_FOUND | cart_id={cart_id} | cause={e}"
        )
        _err(404, "CART_NOT_FOUND", "Cart not found")

    except CartAlreadyCheckedOutException as e:
        logger.warning(
            f"[removeItem] | status_code=409 | error=CART_CHECKED_OUT | cart_id={cart_id} | cause={e}"
        )
        _err(409, "CART_CHECKED_OUT", "Cart already checked out")

    except CartItemNotFoundException as e:
        logger.warning(
            f"[removeItem] | status_code=404 | error=ITEM_NOT_FOUND"
            f" | cart_id={cart_id} | item_id={item_id} | cause={e}"
        )
        _err(404, "ITEM_NOT_FOUND", "Item not found")

    except DatabaseException as e:
        logger.error(
            f"[removeItem] | status_code=503 | error=DATABASE_ERROR"
            f" | cart_id={cart_id} | item_id={item_id} | cause={e}"
        )
        _err(503, "SERVICE_UNAVAILABLE", "Service unavailable")

    except Exception:
        logger.exception(
            f"[removeItem] | status_code=500 | error=INTERNAL_ERROR | cart_id={cart_id} | item_id={item_id}"
        )
        _err(500, "INTERNAL_ERROR", "Unexpected error")


# =========================
# DELETE CART
# =========================
@router.delete("/carts/{cart_id}", response_model=DeleteCartResponse, status_code=200)
def deleteCart(
    cart_id: Annotated[int, Path(gt=0, le=SQLITE_INT_MAX)],
    service: ICartService = Depends(getCartService)
):

    logger.info(f"[deleteCart] | event=request_received | cart_id={cart_id}")

    try:
        service.deleteCart(cart_id)

        logger.info(f"[deleteCart] | status_code=200 | event=cart_deleted | cart_id={cart_id}")

        return {"message": "Cart deleted successfully"}

    except CartNotFoundException as e:
        logger.warning(
            f"[deleteCart] | status_code=404 | error=CART_NOT_FOUND | cart_id={cart_id} | cause={e}"
        )
        _err(404, "CART_NOT_FOUND", "Cart not found")

    except DatabaseException as e:
        logger.error(
            f"[deleteCart] | status_code=503 | error=DATABASE_ERROR | cart_id={cart_id} | cause={e}"
        )
        _err(503, "SERVICE_UNAVAILABLE", "Service unavailable")

    except Exception:
        logger.exception(
            f"[deleteCart] | status_code=500 | error=INTERNAL_ERROR | cart_id={cart_id}"
        )
        _err(500, "INTERNAL_ERROR", "Unexpected error")


# =========================
# CHECKOUT
# =========================
@router.post("/carts/{cart_id}/checkout", response_model=CheckoutResponse, status_code=200)
def checkout(
    cart_id: Annotated[int, Path(gt=0, le=SQLITE_INT_MAX)],
    service: ICartService = Depends(getCartService)
):

    logger.info(f"[checkout] | event=request_received | cart_id={cart_id}")

    try:
        result = service.checkout(cart_id)

        logger.info(f"[checkout] | status_code=200 | event=checkout_success | cart_id={cart_id}")

        return {
            "cart_id": result["cart_id"],
            "status": result["status"],
            "message": "Checkout successful"
        }

    except CartNotFoundException as e:
        logger.warning(
            f"[checkout] | status_code=404 | error=CART_NOT_FOUND | cart_id={cart_id} | cause={e}"
        )
        _err(404, "CART_NOT_FOUND", "Cart not found")

    except CartAlreadyCheckedOutException as e:
        logger.warning(
            f"[checkout] | status_code=409 | error=CART_CHECKED_OUT | cart_id={cart_id} | cause={e}"
        )
        _err(409, "CART_CHECKED_OUT", "Cart already checked out")

    except CartEmptyException as e:
        logger.warning(
            f"[checkout] | status_code=422 | error=CART_EMPTY | cart_id={cart_id} | cause={e}"
        )
        _err(422, "CART_EMPTY", "Cart is empty")

    except DatabaseException as e:
        logger.error(
            f"[checkout] | status_code=503 | error=DATABASE_ERROR | cart_id={cart_id} | cause={e}"
        )
        _err(503, "SERVICE_UNAVAILABLE", "Service unavailable")

    except Exception:
        logger.exception(
            f"[checkout] | status_code=500 | error=INTERNAL_ERROR | cart_id={cart_id}"
        )
        _err(500, "INTERNAL_ERROR", "Unexpected error")
