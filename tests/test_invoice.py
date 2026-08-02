"""
test_invoice.py — Unit tests for the AI Invoice Generator endpoints.

Tests:
  - Create invoice (with and without payment link)
  - QR code generated when payment link provided
  - List invoices (all + filtered)
  - Get invoice by ID
  - Mark invoice as paid
  - Double-paid guard
  - Overdue invoice detection
  - Payment reminder (dry-run)
  - Recurring invoice scheduling
  - PDF download (with QR code)
  - 404 handling
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

INVOICE_PAYLOAD = {
    "company_name":    "Test Corp",
    "company_address": "123 Test St, Karachi",
    "company_email":   "billing@testcorp.com",
    "company_phone":   "+92-300-0000000",
    "client_name":     "Beta Ltd",
    "client_email":    "client@betaltd.com",
    "client_address":  "456 Client Ave, Lahore",
    "line_items": [
        {"description": "Consulting Services", "quantity": 5, "unit_price": 10000, "discount_percent": 0},
        {"description": "Domain & Hosting",    "quantity": 1, "unit_price": 5000,  "discount_percent": 0},
    ],
    "tax_percent":   17,
    "due_date":      "2099-12-31",     # far-future date so it's never overdue in tests
    "payment_link":  "https://pay.testcorp.com/inv-test-001",
    "notes":         "Please pay by the due date.",
}

PAST_DUE_PAYLOAD = {**INVOICE_PAYLOAD, "due_date": "2020-01-01", "payment_link": None}


@pytest.fixture
def created_invoice():
    resp = client.post("/api/v1/invoice/create", json=INVOICE_PAYLOAD)
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture
def past_due_invoice():
    resp = client.post("/api/v1/invoice/create", json=PAST_DUE_PAYLOAD)
    assert resp.status_code == 200
    return resp.json()


# ─────────────────────────────────────────────────────────────────────────────
class TestCreateInvoice:
    def test_create_returns_200(self):
        resp = client.post("/api/v1/invoice/create", json=INVOICE_PAYLOAD)
        assert resp.status_code == 200

    def test_create_has_id_and_number(self, created_invoice):
        assert created_invoice["id"].startswith("INV-")
        assert created_invoice["invoice_number"].startswith("INV-")

    def test_create_status_is_draft(self, created_invoice):
        assert created_invoice["status"] == "draft"

    def test_create_totals_correct(self, created_invoice):
        # 5*10000 + 1*5000 = 55000 subtotal, +17% tax = 64350
        assert created_invoice["subtotal"] == 55000.0
        assert created_invoice["tax_amount"] == pytest.approx(9350.0, rel=1e-3)
        assert created_invoice["total"]     == pytest.approx(64350.0, rel=1e-3)

    def test_qr_code_generated_with_payment_link(self, created_invoice):
        assert created_invoice["qr_code_base64"] is not None
        assert len(created_invoice["qr_code_base64"]) > 100  # base64 string not empty

    def test_no_qr_without_payment_link(self, past_due_invoice):
        assert past_due_invoice["qr_code_base64"] is None


# ─────────────────────────────────────────────────────────────────────────────
class TestListInvoices:
    def test_list_returns_array(self, created_invoice):
        resp = client.get("/api/v1/invoice/list")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_filter_draft(self, created_invoice):
        resp = client.get("/api/v1/invoice/list?status=draft")
        assert resp.status_code == 200
        for inv in resp.json():
            assert inv["status"] == "draft"


# ─────────────────────────────────────────────────────────────────────────────
class TestGetInvoice:
    def test_get_existing(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.get(f"/api/v1/invoice/{inv_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == inv_id

    def test_get_nonexistent_returns_404(self):
        resp = client.get("/api/v1/invoice/INV-DOESNOTEXIST")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestMarkPaid:
    def test_mark_paid_sets_status(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.put(f"/api/v1/invoice/{inv_id}/mark-paid")
        assert resp.status_code == 200
        assert resp.json()["status"] == "paid"

    def test_mark_paid_records_paid_at(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.put(f"/api/v1/invoice/{inv_id}/mark-paid")
        assert resp.json()["paid_at"] is not None

    def test_double_paid_returns_400(self, created_invoice):
        inv_id = created_invoice["id"]
        client.put(f"/api/v1/invoice/{inv_id}/mark-paid")
        resp = client.put(f"/api/v1/invoice/{inv_id}/mark-paid")
        assert resp.status_code == 400

    def test_mark_paid_nonexistent_returns_404(self):
        resp = client.put("/api/v1/invoice/INV-DOESNOTEXIST/mark-paid")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestOverdueInvoice:
    def test_overdue_endpoint_returns_array(self, past_due_invoice):
        resp = client.get("/api/v1/invoice/overdue")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_overdue_contains_past_due_invoice(self, past_due_invoice):
        resp = client.get("/api/v1/invoice/overdue")
        ids = [inv["id"] for inv in resp.json()]
        assert past_due_invoice["id"] in ids

    def test_overdue_status_flagged(self, past_due_invoice):
        resp = client.get(f"/api/v1/invoice/{past_due_invoice['id']}")
        assert resp.json()["status"] == "overdue"


# ─────────────────────────────────────────────────────────────────────────────
class TestPaymentReminder:
    def test_reminder_returns_200(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.post(f"/api/v1/invoice/{inv_id}/payment-reminder")
        assert resp.status_code == 200

    def test_reminder_message_present(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.post(f"/api/v1/invoice/{inv_id}/payment-reminder")
        assert "message" in resp.json()

    def test_reminder_paid_invoice_returns_400(self, created_invoice):
        inv_id = created_invoice["id"]
        client.put(f"/api/v1/invoice/{inv_id}/mark-paid")
        resp = client.post(f"/api/v1/invoice/{inv_id}/payment-reminder")
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
class TestRecurringInvoice:
    def test_create_recurring_returns_200(self, created_invoice):
        inv_id = created_invoice["id"]
        payload = {
            "base_invoice_id": inv_id,
            "frequency": "monthly",
            "start_date": "2026-09-01",
        }
        resp = client.post("/api/v1/invoice/recurring", json=payload)
        assert resp.status_code == 200

    def test_create_recurring_has_id(self, created_invoice):
        inv_id = created_invoice["id"]
        payload = {
            "base_invoice_id": inv_id,
            "frequency": "monthly",
            "start_date": "2026-09-01",
        }
        resp = client.post("/api/v1/invoice/recurring", json=payload)
        assert resp.json()["recurring_id"].startswith("REC-")

    def test_create_recurring_nonexistent_base_returns_404(self):
        payload = {
            "base_invoice_id": "INV-DOESNOTEXIST",
            "frequency": "monthly",
            "start_date": "2026-09-01",
        }
        resp = client.post("/api/v1/invoice/recurring", json=payload)
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestInvoicePDF:
    def test_pdf_returns_200(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.get(f"/api/v1/invoice/{inv_id}/pdf")
        assert resp.status_code == 200

    def test_pdf_content_type(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.get(f"/api/v1/invoice/{inv_id}/pdf")
        assert resp.headers["content-type"] == "application/pdf"

    def test_pdf_has_content(self, created_invoice):
        inv_id = created_invoice["id"]
        resp = client.get(f"/api/v1/invoice/{inv_id}/pdf")
        assert len(resp.content) > 1000

    def test_pdf_nonexistent_returns_404(self):
        resp = client.get("/api/v1/invoice/INV-DOESNOTEXIST/pdf")
        assert resp.status_code == 404
