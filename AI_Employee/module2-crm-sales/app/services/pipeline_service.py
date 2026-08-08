from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.pipeline_stage import PipelineStage


class PipelineService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_stage(self, payload: dict[str, Any]) -> PipelineStage:
        stage = PipelineStage(**payload)
        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)
        return stage

    def list_stages(self) -> list[PipelineStage]:
        return self.db.scalars(select(PipelineStage).where(PipelineStage.deleted_at.is_(None)).order_by(PipelineStage.order)).all()

    def create_deal(self, payload: dict[str, Any]) -> Deal:
        deal = Deal(**payload)
        self.db.add(deal)
        self.db.commit()
        self.db.refresh(deal)
        return deal

    def list_deals(self, stage: str | None = None, owner_id: str | None = None, skip: int = 0, limit: int = 20) -> tuple[list[Deal], int]:
        query = self.db.query(Deal).filter(Deal.deleted_at.is_(None))
        if stage:
            query = query.filter(Deal.stage == stage)
        if owner_id:
            query = query.filter(Deal.owner_id == owner_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def update_deal_stage(self, deal: Deal, stage: str) -> Deal:
        deal.stage = stage
        self.db.commit()
        self.db.refresh(deal)
        return deal
