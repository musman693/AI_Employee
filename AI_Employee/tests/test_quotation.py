"""
test_quotation.py — Unit tests for the AI Quotation Generator endpoints.

Tests:
  - Create a quotation
  - List quotations (all + filtered by status)
  - Get a quotation by ID
  - Approve a quotation
  - Reject a quotation
  - Double-approve / double-reject guard
  - Send email (dry-run)
  - Download PDF
  - 404 handling
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── Shared test payload ───────────────────────────────────────────────────────
QUOTATION_PAYLOAD = {
    "branding": {
        "company_name": "Test Corp",
        "address": "123 Test St, Karachi",
        "phone": "+92-300-0000000",
        "email": "billing@testcorp.com",
        "website": "https://testcorp.com",
    },
    "client_name": "Alpha Ltd",
    "client_email": "client@alphaltd.com",
    "client_address": "456 Client Ave, Lahore",
    "line_items": [
        {"description": "Website Development", "quantity": 1, "unit_price": 200000, "discount_percent": 10},
        {"description": "Monthly SEO",          "quantity": 3, "unit_price": 15000,  "discount_percent": 0},
    ],
    "tax_percent": 17,
    "global_discount_percent": 5,
    "valid_until": "2026-12-31",
    "notes": "Payment due within 30 days.",
    "payment_terms": "Net 30",
}


@pytest.fixture
def created_quotation():
    """Create a quotation and return the response JSON."""
    resp = client.post("/api/v1/quotation/create", json=QUOTATION_PAYLOAD)
    assert resp.status_code == 200
    return resp.json()


# ─────────────────────────────────────────────────────────────────────────────
class TestCreateQuotation:
    def test_create_returns_200(self):
        resp = client.post("/api/v1/quotation/create", json=QUOTATION_PAYLOAD)
        assert resp.status_code == 200

    def test_create_returns_id(self, created_quotation):
        assert "id" in created_quotation
        assert created_quotation["id"].startswith("QUO-")

    def test_create_status_is_draft(self, created_quotation):
        assert created_quotation["status"] == "draft"

    def test_create_totals_computed(self, created_quotation):
        assert created_quotation["subtotal"] > 0
        assert created_quotation["total"] > created_quotation["subtotal"]  # tax was applied
        assert created_quotation["tax_amount"] > 0
        assert created_quotation["discount_amount"] > 0

    def test_create_client_fields(self, created_quotation):
        assert created_quotation["client_name"] == "Alpha Ltd"
        assert created_quotation["client_email"] == "client@alphaltd.com"

    def test_create_branding_fields(self, created_quotation):
        assert created_quotation["branding"]["company_name"] == "Test Corp"


# ─────────────────────────────────────────────────────────────────────────────
class TestListQuotations:
    def test_list_returns_array(self, created_quotation):
        resp = client.get("/api/v1/quotation/list")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_filter_by_status(self, created_quotation):
        resp = client.get("/api/v1/quotation/list?status=draft")
        assert resp.status_code == 200
        for q in resp.json():
            assert q["status"] == "draft"


# ─────────────────────────────────────────────────────────────────────────────
class TestGetQuotation:
    def test_get_existing(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.get(f"/api/v1/quotation/{q_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == q_id

    def test_get_nonexistent_returns_404(self):
        resp = client.get("/api/v1/quotation/QUO-DOESNOTEXIST")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestApproveQuotation:
    def test_approve_sets_status(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.put(f"/api/v1/quotation/{q_id}/approve")
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    def test_double_approve_returns_400(self, created_quotation):
        q_id = created_quotation["id"]
        client.put(f"/api/v1/quotation/{q_id}/approve")
        resp = client.put(f"/api/v1/quotation/{q_id}/approve")
        assert resp.status_code == 400

    def test_approve_nonexistent_returns_404(self):
        resp = client.put("/api/v1/quotation/QUO-DOESNOTEXIST/approve")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestRejectQuotation:
    def test_reject_sets_status(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.put(f"/api/v1/quotation/{q_id}/reject")
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    def test_double_reject_returns_400(self, created_quotation):
        q_id = created_quotation["id"]
        client.put(f"/api/v1/quotation/{q_id}/reject")
        resp = client.put(f"/api/v1/quotation/{q_id}/reject")
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
class TestSendEmail:
    def test_send_email_dry_run(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.post(f"/api/v1/quotation/{q_id}/send-email", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert data["recipient_email"] == "client@alphaltd.com"

    def test_send_email_custom_recipient(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.post(f"/api/v1/quotation/{q_id}/send-email",
                           json={"recipient_email": "custom@test.com"})
        assert resp.status_code == 200
        assert resp.json()["recipient_email"] == "custom@test.com"


# ─────────────────────────────────────────────────────────────────────────────
class TestDownloadPDF:
    def test_pdf_returns_200(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.get(f"/api/v1/quotation/{q_id}/pdf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"

    def test_pdf_has_content(self, created_quotation):
        q_id = created_quotation["id"]
        resp = client.get(f"/api/v1/quotation/{q_id}/pdf")
        assert len(resp.content) > 1000   # A real PDF will be at least a few KB

    def test_pdf_nonexistent_returns_404(self):
        resp = client.get("/api/v1/quotation/QUO-DOESNOTEXIST/pdf")
        assert resp.status_code == 404
