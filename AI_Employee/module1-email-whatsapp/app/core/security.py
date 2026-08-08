from typing import Any

from fastapi import Depends, Header, HTTPException, status


async def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> dict[str, Any]:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
        )
    return {"user_id": x_user_id}


CurrentUser = Depends(get_current_user)
