from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.activity_routes import router as activity_router
from app.api.customer_routes import router as customer_router
from app.api.deal_routes import router as deal_router
from app.api.lead_routes import router as lead_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("crm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("CRM app initialized")
    yield
    logger.info("CRM app shutting down")


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": "http_error", "detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "validation_error", "detail": exc.errors()})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "detail": str(exc)})


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(customer_router)
app.include_router(lead_router)
app.include_router(deal_router)
app.include_router(activity_router)


@app.get("/pipeline")
async def list_pipeline() -> list[dict[str, object]]:
    from app.models.pipeline_stage import PipelineStage
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        stages = db.query(PipelineStage).filter(PipelineStage.deleted_at.is_(None)).order_by(PipelineStage.order).all()
        return [{"id": stage.id, "name": stage.name, "order": stage.order, "is_won": stage.is_won, "is_lost": stage.is_lost} for stage in stages]
    finally:
        db.close()
