from typing import Any


class GmailService:
    async def login(self) -> dict[str, Any]:
        return {"status": "ok", "provider": "gmail"}

    async def read_inbox(self) -> list[dict[str, Any]]:
        return []

    async def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        return {"status": "sent", "to": to, "subject": subject}

    async def watch_for_new_mail(self) -> dict[str, Any]:
        return {"status": "watching"}
