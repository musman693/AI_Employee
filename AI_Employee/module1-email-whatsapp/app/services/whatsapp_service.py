from typing import Any


class WhatsAppService:
    async def receive_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "received", "payload": payload}

    async def send_text_message(self, to: str, message: str) -> dict[str, Any]:
        return {"status": "sent", "to": to, "message": message}

    async def send_template_message(self, to: str, template: str, components: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"status": "sent", "to": to, "template": template}

    async def send_media_message(self, to: str, media_url: str) -> dict[str, Any]:
        return {"status": "sent", "to": to, "media_url": media_url}
