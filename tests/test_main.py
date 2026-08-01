from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_legal_analysis():
    res = client.post("/api/v1/legal/analyze-contract", json={"contract_text": "Sample liability text"})
    assert res.status_code == 200