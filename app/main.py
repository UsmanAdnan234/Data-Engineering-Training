from fastapi import FastAPI
from app.api.cart import router as cart_router

app = FastAPI()

app.include_router(cart_router)