from fastapi import APIRouter, HTTPException
from app.schemas.cart import (
    CreateCartRequest,
    CreateCartResponse
)

from app.services.cart_service import CartService

from app.database.connection import get_connection

from app.core.logger import logger

from app.core.exceptions import (
    UserNotFoundException,
    CartAlreadyExistsException
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

        logger.info(
            f"Create cart request user_id={payload.user_id}"
        )

        service = CartService(conn)

        result = service.create_cart(
            payload.user_id
        )

        logger.info(
            f"Cart created cart_id={result['cart_id']}"
        )

        return {
            "cart_id": result["cart_id"],
            "user_id": result["user_id"],
            "message": "Cart created successfully"
        }

    except UserNotFoundException:

        logger.warning(
            f"User not found user_id={payload.user_id}"
        )

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    except CartAlreadyExistsException:

        logger.warning(
            f"Cart already exists user_id={payload.user_id}"
        )

        raise HTTPException(
            status_code=409,
            detail="Cart already exists"
        )

    except Exception as e:

        logger.exception(
            f"Unexpected error while creating cart"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        conn.close()