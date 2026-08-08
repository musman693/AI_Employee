from __future__ import annotations

from typing import Any

from app.models.activity import Activity
from app.models.customer import Customer
from app.models.deal import Deal
from app.services.ai_provider import AIProvider


class InsightsService:
    def __init__(self, ai_provider: AIProvider | None = None) -> None:
        self.ai_provider = ai_provider or AIProvider()

    async def summarize_customer(self, customer: Customer, activities: list[Activity], deals: list[Deal]) -> str:
        context = f"Customer {customer.name} had {len(activities)} activities and {len(deals)} deals"
        return await self.ai_provider.generate_summary(context)

    async def build_insights(self, customer: Customer, activities: list[Activity], deals: list[Deal]) -> dict[str, Any]:
        context = f"Customer {customer.name} had {len(activities)} activities and {len(deals)} deals"
        return await self.ai_provider.generate_insights(context)
