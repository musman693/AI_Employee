import pytest

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


@pytest.mark.asyncio
async def test_email_draft_endpoint():
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/email/draft",
            json={"instruction": "Write a follow-up email to a client"},
            headers={"X-User-Id": "tester"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert "subject" in payload
    assert "body" in payload


@pytest.mark.asyncio
async def test_whatsapp_support_reply_endpoint():
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/whatsapp/support-reply",
            json={"message": "I need help with my order", "customer_name": "Ada"},
            headers={"X-User-Id": "tester"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert "reply" in payload
