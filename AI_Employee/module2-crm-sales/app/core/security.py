from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.rbac import require_permission

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, str]:
    if credentials is None:
        return {"role": "ai_sales_manager", "user_id": "demo-user"}
    return {"role": "ai_sales_manager", "user_id": "demo-user"}


async def get_current_user_with_permission(permission: str) -> dict[str, str]:
    user = await get_current_user()
    require_permission(user, permission)
    return user
