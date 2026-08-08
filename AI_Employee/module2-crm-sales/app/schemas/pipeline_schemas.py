from __future__ import annotations

from pydantic import BaseModel, Field


class PipelineStageCreate(BaseModel):
    name: str = Field(..., min_length=1)
    order: int = 0
    is_won: bool = False
    is_lost: bool = False


class PipelineStageRead(BaseModel):
    id: int
    name: str
    order: int
    is_won: bool
    is_lost: bool

    model_config = {"from_attributes": True}


class PipelineStageListResponse(BaseModel):
    items: list[PipelineStageRead]
    total: int
