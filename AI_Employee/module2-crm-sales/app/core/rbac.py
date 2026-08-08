from __future__ import annotations

from fastapi import HTTPException, status

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "ai_sales_manager": {
        "customers:read",
        "customers:write",
        "leads:read",
        "leads:write",
        "deals:read",
        "deals:write",
        "activities:read",
        "activities:write",
        "pipeline:read",
        "pipeline:write",
        "insights:read",
        "insights:write",
    },
    "ai_ceo_assistant": {
        "customers:read",
        "leads:read",
        "deals:read",
        "activities:read",
        "pipeline:read",
        "insights:read",
    },
}


def require_permission(user: dict[str, str], permission: str) -> None:
    role = user.get("role", "")
    allowed = ROLE_PERMISSIONS.get(role, set())
    if permission not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
