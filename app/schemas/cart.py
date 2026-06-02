from pydantic import BaseModel

class CreateCartRequest(BaseModel):
    user_id: int


class CreateCartResponse(BaseModel):
    cart_id: int
    user_id: int
    message: str