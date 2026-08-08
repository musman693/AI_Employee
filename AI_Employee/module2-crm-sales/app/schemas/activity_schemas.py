from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    customer_id: int | None = None
    lead_id: int | None = None
    activity_type: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    created_by: str | None = None


class ActivityRead(BaseModel):
    id: int
    customer_id: int | None = None
    lead_id: int | None = None
    activity_type: str
    content: str
    created_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    items: list[ActivityRead]
    total: int
