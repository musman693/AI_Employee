from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class DealCreate(BaseModel):
    customer_id: int | None = None
    title: str = Field(..., min_length=1)
    value: float | None = None
    stage: str | None = None
    probability: int | None = None
    expected_close_date: date | None = None
    owner_id: str | None = None


class DealUpdate(BaseModel):
    stage: str | None = None
    probability: int | None = None
    owner_id: str | None = None


class DealRead(BaseModel):
    id: int
    customer_id: int | None = None
    title: str
    value: float | None = None
    stage: str
    probability: int | None = None
    expected_close_date: date | None = None
    owner_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DealListResponse(BaseModel):
    items: list[DealRead]
    total: int
