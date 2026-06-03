from pydantic import BaseModel, Field


SQLITE_INT_MAX = 9223372036854775807


class CreateCartRequest(BaseModel):
    user_id: int = Field(gt=0, le=SQLITE_INT_MAX)


class CreateCartResponse(BaseModel):
    cart_id: int
    user_id: int
    message: str


class AddCartItemRequest(BaseModel):
    variant_id: int = Field(gt=0, le=SQLITE_INT_MAX)
    quantity: int = Field(gt=0)


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
