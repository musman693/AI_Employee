from __future__ import annotations

from typing import Any


class AIProvider:
    async def generate_summary(self, context: str) -> str:
        return f"AI summary for: {context[:120]}"

    async def generate_insights(self, context: str) -> dict[str, Any]:
        return {
            "risk": "No recent contact",
            "next_best_action": "Send a follow-up email",
            "context": context[:120],
        }
