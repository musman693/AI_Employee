from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1)
    company: str | None = None
    email: str | None = None
    source: str | None = None
    status: str | None = None
    score: int | None = None
    assigned_to: str | None = None


class LeadUpdate(BaseModel):
    status: str | None = None
    assigned_to: str | None = None
    score: int | None = None


class LeadRead(BaseModel):
    id: int
    name: str
    company: str | None = None
    email: str | None = None
    source: str | None = None
    status: str
    score: int | None = None
    assigned_to: str | None = None
    converted_customer_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadConvertResponse(BaseModel):
    lead: LeadRead
    customer: dict[str, object]
