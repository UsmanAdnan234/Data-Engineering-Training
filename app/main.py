from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.api.cart import router as cartRouter
from app.core.logger import logger

app = FastAPI()

app.include_router(cartRouter)


@app.get("/health")
async def health():
    return {"status": "ok"}


def _friendlyMessage(errType: str, ctx: dict | None) -> str:
    ctx = ctx or {}
    messages = {
        "int_parsing":        "Must be a valid integer",
        "int_type":           "Must be a valid integer",
        "float_type":         "Must be a valid number",
        "int_from_float":     "Must be a valid integer (no decimal allowed)",
        "string_type":        "Must be text",
        "bool_type":          "Must be true or false",
        "missing":            "This field is required",
        "greater_than":       f"Must be greater than {ctx.get('gt', 0)}",
        "greater_than_equal": f"Must be {ctx.get('ge', 0)} or greater",
        "less_than_equal":    "Value is out of valid range",
        "less_than":          f"Must be less than {ctx.get('lt', 0)}",
    }
    return messages.get(errType, "Invalid value")


def _friendlyField(loc: tuple) -> str:
    parts = [str(p) for p in loc if p not in ("body", "query", "path")]
    return ".".join(parts) if parts else "field"


@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    rawErrors = exc.errors()

    details = [
        {
            "field": _friendlyField(err["loc"]),
            "message": _friendlyMessage(err["type"], err.get("ctx"))
        }
        for err in rawErrors
    ]

    logger.warning(
        f"[validationError] | status_code=422 | error=VALIDATION_ERROR"
        f" | method={request.method} | path={request.url.path}"
        f" | fields={[d['field'] for d in details]} | raw={rawErrors}"
    )

    return JSONResponse(
        status_code=422,
        content={"error": "VALIDATION_ERROR", "details": details}
    )


@app.exception_handler(HTTPException)
async def httpExceptionHandler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        # Our own structured errors — already logged in the API function before _err() was called
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    # FastAPI-internal errors (405 Method Not Allowed, 404 unknown route, etc.)
    logger.warning(
        f"[httpError] | status_code={exc.status_code} | error=HTTP_ERROR"
        f" | method={request.method} | path={request.url.path} | detail={exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP_ERROR", "message": str(exc.detail)}
    )
