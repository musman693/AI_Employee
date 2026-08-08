from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    tags: list[str] | None = None
    owner_id: str | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    company: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    tags: list[str] | None = None
    owner_id: str | None = None
    notes: str | None = None


class CustomerRead(BaseModel):
    id: int
    name: str
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    tags: list[str] | None = None
    owner_id: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    items: list[CustomerRead]
    total: int
