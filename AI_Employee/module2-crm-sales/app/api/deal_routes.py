from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from datetime import datetime

from app.core.security import get_current_user_with_permission
from app.db.session import get_db
from app.models.deal import Deal
from app.schemas.deal_schemas import DealCreate, DealListResponse, DealRead, DealUpdate
from app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=DealRead, status_code=status.HTTP_201_CREATED)
async def create_deal(
    payload: DealCreate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("deals:write")),
) -> DealRead:
    service = PipelineService(db)
    deal = service.create_deal(payload.model_dump())
    return DealRead.model_validate(deal)


@router.get("", response_model=DealListResponse)
async def list_deals(
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("deals:read")),
    stage: str | None = Query(default=None),
    owner: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    skip: int = 0,
    limit: int = 20,
) -> DealListResponse:
    service = PipelineService(db)
    items, total = service.list_deals(stage=stage, owner_id=owner, skip=skip, limit=limit)
    return DealListResponse(items=[DealRead.model_validate(item) for item in items], total=total)


@router.patch("/{deal_id}", response_model=DealRead)
async def update_deal(
    deal_id: int,
    payload: DealUpdate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("deals:write")),
) -> DealRead:
    deal = db.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(deal, key, value)
    db.commit()
    db.refresh(deal)
    return DealRead.model_validate(deal)


@router.post("/{deal_id}/stage", response_model=DealRead)
async def update_deal_stage(
    deal_id: int,
    stage: str,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("deals:write")),
) -> DealRead:
    deal = db.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    deal.stage = stage
    db.commit()
    db.refresh(deal)
    return DealRead.model_validate(deal)

@router.get("/pipeline")
async def list_pipeline_stages(
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("pipeline:read")),
) -> list[dict[str, object]]:
    from app.models.pipeline_stage import PipelineStage
    stages = db.query(PipelineStage).filter(PipelineStage.deleted_at.is_(None)).order_by(PipelineStage.order).all()
    return [{"id": stage.id, "name": stage.name, "order": stage.order, "is_won": stage.is_won, "is_lost": stage.is_lost} for stage in stages]
