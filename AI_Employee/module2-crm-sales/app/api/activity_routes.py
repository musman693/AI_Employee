from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_with_permission
from app.db.session import get_db
from app.models.activity import Activity
from app.schemas.activity_schemas import ActivityCreate, ActivityListResponse, ActivityRead

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
async def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("activities:write")),
) -> ActivityRead:
    activity = Activity(**payload.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return ActivityRead.model_validate(activity)


@router.get("", response_model=ActivityListResponse)
async def list_activities(
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("activities:read")),
    customer_id: int | None = None,
    lead_id: int | None = None,
    activity_type: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> ActivityListResponse:
    query = db.query(Activity).filter(Activity.deleted_at.is_(None))
    if customer_id is not None:
        query = query.filter(Activity.customer_id == customer_id)
    if lead_id is not None:
        query = query.filter(Activity.lead_id == lead_id)
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    activities = query.offset(skip).limit(limit).all()
    return ActivityListResponse(items=[ActivityRead.model_validate(activity) for activity in activities], total=query.count())
