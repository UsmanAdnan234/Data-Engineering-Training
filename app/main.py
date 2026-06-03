from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.cart import router as cartRouter
from app.core.logger import logger

app = FastAPI()

app.include_router(cartRouter)


@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"]
        }
        for err in exc.errors()
    ]

    logger.warning(
        f"[validationError] Invalid request | {request.method} {request.url.path} | errors={errors}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request data",
            "errors": errors
        }
    )
