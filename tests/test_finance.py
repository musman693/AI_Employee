"""
test_finance.py — Unit tests for the AI Finance Assistant & AI Accountant endpoints.

Tests:
  - Finance summary (empty state + with paid invoices)
  - Forecast (default + custom period)
  - Accountant report structure
  - Transaction categorization (known keywords + miscellaneous fallback)
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── Helper: create and pay an invoice so finance endpoints have real data ─────
INVOICE_PAYLOAD = {
    "company_name":    "Finance Test Corp",
    "company_address": "1 Finance St",
    "company_email":   "billing@fintest.com",
    "company_phone":   "+92-300-9999999",
    "client_name":     "Gamma Ltd",
    "client_email":    "client@gammaltd.com",
    "line_items": [
        {"description": "Consulting", "quantity": 1, "unit_price": 100000, "discount_percent": 0},
    ],
    "tax_percent": 17,
    "due_date": "2099-12-31",
}


@pytest.fixture
def paid_invoice():
    """Create and immediately mark an invoice as paid to seed finance data."""
    create_resp = client.post("/api/v1/invoice/create", json=INVOICE_PAYLOAD)
    assert create_resp.status_code == 200
    inv_id = create_resp.json()["id"]
    pay_resp = client.put(f"/api/v1/invoice/{inv_id}/mark-paid")
    assert pay_resp.status_code == 200
    return create_resp.json()


# ─────────────────────────────────────────────────────────────────────────────
class TestFinanceSummary:
    def test_summary_returns_200(self):
        resp = client.get("/api/v1/finance/summary")
        assert resp.status_code == 200

    def test_summary_schema_fields(self):
        resp = client.get("/api/v1/finance/summary")
        data = resp.json()
        required_fields = [
            "period", "total_revenue", "total_expenses",
            "net_profit", "profit_margin_percent",
            "outstanding_invoices", "overdue_invoices", "ai_insight"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_summary_empty_state_message(self):
        resp = client.get("/api/v1/finance/summary")
        data = resp.json()
        assert isinstance(data["ai_insight"], str)
        assert len(data["ai_insight"]) > 0

    def test_summary_with_paid_invoice(self, paid_invoice):
        resp = client.get("/api/v1/finance/summary")
        data = resp.json()
        # After paying a 117,000 invoice, revenue should be at least that
        assert data["total_revenue"] >= 117000.0
        assert data["net_profit"] > 0

    def test_summary_custom_period(self):
        resp = client.get("/api/v1/finance/summary?period=last_month")
        assert resp.status_code == 200
        assert resp.json()["period"] == "last_month"


# ─────────────────────────────────────────────────────────────────────────────
class TestFinanceForecast:
    def test_forecast_returns_200(self):
        resp = client.get("/api/v1/finance/forecast")
        assert resp.status_code == 200

    def test_forecast_schema_fields(self):
        resp = client.get("/api/v1/finance/forecast")
        data = resp.json()
        required_fields = [
            "period", "projected_revenue", "projected_expenses",
            "projected_profit", "confidence_percent",
            "ai_analysis", "recommendations"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_forecast_recommendations_is_list(self):
        resp = client.get("/api/v1/finance/forecast")
        assert isinstance(resp.json()["recommendations"], list)

    def test_forecast_custom_period(self):
        resp = client.get("/api/v1/finance/forecast?period=next_quarter")
        assert resp.status_code == 200
        assert resp.json()["period"] == "next_quarter"

    def test_forecast_confidence_in_range(self):
        resp = client.get("/api/v1/finance/forecast")
        confidence = resp.json()["confidence_percent"]
        assert 0 <= confidence <= 100


# ─────────────────────────────────────────────────────────────────────────────
class TestAccountantReport:
    def test_report_returns_200(self):
        resp = client.get("/api/v1/finance/accountant/report")
        assert resp.status_code == 200

    def test_report_schema_fields(self):
        resp = client.get("/api/v1/finance/accountant/report")
        data = resp.json()
        required_fields = [
            "report_id", "generated_at", "period",
            "income_summary", "expense_summary",
            "net_position", "tax_liability_estimate", "ai_notes"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_report_id_has_prefix(self):
        resp = client.get("/api/v1/finance/accountant/report")
        assert resp.json()["report_id"].startswith("RPT-")

    def test_report_with_paid_invoice(self, paid_invoice):
        resp = client.get("/api/v1/finance/accountant/report")
        data = resp.json()
        assert data["net_position"] > 0
        assert data["tax_liability_estimate"] > 0

    def test_report_custom_period(self):
        resp = client.get("/api/v1/finance/accountant/report?period=ytd")
        assert resp.status_code == 200
        assert resp.json()["period"] == "ytd"


# ─────────────────────────────────────────────────────────────────────────────
class TestCategorizeTransaction:
    def _categorize(self, description: str, amount: float = 1000, tx_type=None):
        payload = {"description": description, "amount": amount}
        if tx_type:
            payload["transaction_type"] = tx_type
        return client.post("/api/v1/finance/accountant/categorize", json=payload)

    def test_categorize_returns_200(self):
        resp = self._categorize("Monthly salary for staff")
        assert resp.status_code == 200

    def test_salary_keyword(self):
        resp = self._categorize("Employee salary payment")
        assert resp.json()["suggested_category"] == "salary"

    def test_utilities_keyword(self):
        resp = self._categorize("Electricity bill for office")
        assert resp.json()["suggested_category"] == "utilities"

    def test_marketing_keyword(self):
        resp = self._categorize("Facebook ads campaign spend")
        assert resp.json()["suggested_category"] == "marketing"

    def test_rent_keyword(self):
        resp = self._categorize("Office lease payment for September")
        assert resp.json()["suggested_category"] == "rent"

    def test_sales_keyword(self):
        resp = self._categorize("Client invoice payment received")
        assert resp.json()["suggested_category"] == "sales"

    def test_refund_keyword(self):
        resp = self._categorize("Customer refund processed")
        assert resp.json()["suggested_category"] == "refund"

    def test_miscellaneous_fallback(self):
        resp = self._categorize("Random unidentifiable expense xyz123")
        assert resp.json()["suggested_category"] == "miscellaneous"

    def test_response_has_confidence(self):
        resp = self._categorize("Salary for development team")
        assert "confidence_percent" in resp.json()

    def test_response_has_reasoning(self):
        resp = self._categorize("Monthly rent")
        assert "ai_reasoning" in resp.json()
        assert len(resp.json()["ai_reasoning"]) > 0

    def test_explicit_transaction_type(self):
        resp = self._categorize("Consulting revenue", tx_type="income")
        assert resp.json()["transaction_type"] == "income"
