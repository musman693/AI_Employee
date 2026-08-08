import asyncio
import logging
import os
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger("ai_employee_module1")
settings = get_settings()


class AIProviderError(RuntimeError):
    pass


async def _run_with_retry(func: Any, *args: Any, **kwargs: Any) -> Any:
    last_error: Exception | None = None
    for attempt in range(settings.ai_max_retries):
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=settings.ai_timeout_seconds)
        except Exception as exc:  # pragma: no cover - retry wrapper
            last_error = exc
            logger.warning("AI call failed", extra={"attempt": attempt + 1, "error": str(exc)})
            if attempt == settings.ai_max_retries - 1:
                raise AIProviderError(str(exc)) from exc
            await asyncio.sleep(0.2 * (attempt + 1))
    raise AIProviderError("AI call failed") from last_error


async def generate_reply(prompt: str, *, context: str | None = None) -> str:
    async def _call() -> str:
        provider = settings.ai_provider.lower()
        if provider == "anthropic":
            return f"[anthropic] {prompt}"
        return f"[openai] {prompt}"

    return await _run_with_retry(_call)


async def summarize(messages: list[str]) -> str:
    async def _call() -> str:
        joined = "\n".join(messages)
        return f"Summary of {len(messages)} messages: {joined[:220]}"

    return await _run_with_retry(_call)


async def classify(subject: str, body: str) -> tuple[str, float]:
    async def _call() -> tuple[str, float]:
        lowered = f"{subject} {body}".lower()
        if "urgent" in lowered:
            return "urgent", 0.92
        if "spam" in lowered:
            return "spam", 0.95
        if "support" in lowered:
            return "support", 0.9
        if "sale" in lowered or "sales" in lowered:
            return "sales", 0.88
        return "internal", 0.72

    return await _run_with_retry(_call)


async def prioritize(emails: list[str]) -> list[dict[str, Any]]:
    async def _call() -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []
        for index, email in enumerate(emails):
            score = max(1, 10 - index)
            ranked.append({"email": email, "score": score})
        return ranked

    return await _run_with_retry(_call)


async def follow_up_suggestion(instruction: str) -> str:
    async def _call() -> str:
        return f"Follow-up suggestion based on: {instruction}"

    return await _run_with_retry(_call)
