import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def reset_db() -> None:
    from app.db.base import Base
    from app.db.session import engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_customer(client: TestClient) -> None:
    payload = {
        "name": "Alice Johnson",
        "company": "Contoso",
        "email": "alice@example.com",
        "phone": "+15551234567",
        "tags": ["vip"]
    }
    response = client.post("/customers", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["company"] == payload["company"]


def test_list_customers(client: TestClient) -> None:
    response = client.get("/customers")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_create_lead_and_convert(client: TestClient) -> None:
    lead_payload = {
        "name": "Bob Smith",
        "company": "Northwind",
        "email": "bob@example.com",
        "source": "website",
        "status": "new",
        "score": 80,
        "assigned_to": "sales-agent"
    }
    response = client.post("/leads", json=lead_payload)
    assert response.status_code == 201
    lead = response.json()
    assert lead["name"] == lead_payload["name"]

    convert_response = client.post(f"/leads/{lead['id']}/convert")
    assert convert_response.status_code == 200
