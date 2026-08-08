import logging
import time
import uuid
from contextvars import ContextVar
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.email_routes import router as email_router
from app.api.whatsapp_routes import router as whatsapp_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_employee_module1")

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


app = FastAPI(
    title="AI Email & WhatsApp Assistant",
    description="Backend service for AI Email and WhatsApp assistant workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(email_router, prefix="", tags=["Email"])
app.include_router(whatsapp_router, prefix="", tags=["WhatsApp"])


@app.middleware("http")
async def add_request_context(request: Request, call_next: Callable) -> JSONResponse:
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    token = request_id_ctx.set(request_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Unhandled exception", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "detail": "Unexpected server error"},
        )
    finally:
        request_id_ctx.reset(token)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request_completed",
        extra={"request_id": request_id, "method": request.method, "path": request.url.path, "duration_ms": elapsed_ms},
    )
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.__class__.__name__, "detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "validation_error", "detail": str(exc)})
