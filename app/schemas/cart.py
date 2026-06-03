from pydantic import BaseModel, Field

_MAX_ID = 2_147_483_647
_MAX_QUANTITY = 10_000


class CreateCartRequest(BaseModel):
    user_id: int = Field(gt=0, le=_MAX_ID)


class CreateCartResponse(BaseModel):
    cart_id: int
    user_id: int
    message: str


class AddCartItemRequest(BaseModel):
    variant_id: int = Field(gt=0, le=_MAX_ID)
    quantity: int = Field(gt=0, le=_MAX_QUANTITY)


class AddCartItemResponse(BaseModel):
    item_id: int
    cart_id: int
    variant_id: int
    quantity: int
    message: str


class RemoveCartItemResponse(BaseModel):
    message: str


class DeleteCartResponse(BaseModel):
    message: str


class CheckoutResponse(BaseModel):
    cart_id: int
    status: str
    message: str
