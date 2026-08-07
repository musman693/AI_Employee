"""
test_report.py — Unit tests for the AI Reporting endpoints.

Tests:
  - Sales analytics (response structure, fields)
  - Revenue report (response structure, projections)
  - Expense report (response structure, categories)
  - Customer analytics (response structure, segmentation)
  - Revenue forecast (response structure, scenarios)
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
class TestSalesAnalytics:
    def test_sales_analytics_returns_200(self):
        resp = client.get("/api/v1/report/sales")
        assert resp.status_code == 200

    def test_sales_analytics_schema_fields(self):
        resp = client.get("/api/v1/report/sales")
        data = resp.json()
        required_fields = [
            "period", "generated_at", "total_sales", "total_orders",
            "average_order_value", "sales_by_month", "top_products",
            "sales_by_channel", "conversion_rate_percent", "growth_rate_percent",
            "ai_insights", "recommendations"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_sales_analytics_has_recommendations_list(self):
        resp = client.get("/api/v1/report/sales")
        assert isinstance(resp.json()["recommendations"], list)

    def test_sales_analytics_custom_period(self):
        resp = client.get("/api/v1/report/sales?period=last_month")
        assert resp.status_code == 200
        assert resp.json()["period"] == "last_month"

    def test_sales_analytics_total_sales_is_number(self):
        resp = client.get("/api/v1/report/sales")
        assert isinstance(resp.json()["total_sales"], (int, float))

    def test_sales_analytics_growth_rate(self):
        resp = client.get("/api/v1/report/sales")
        growth = resp.json()["growth_rate_percent"]
        assert growth is None or isinstance(growth, (int, float))


# ─────────────────────────────────────────────────────────────────────────────
class TestRevenueReport:
    def test_revenue_report_returns_200(self):
        resp = client.get("/api/v1/report/revenue")
        assert resp.status_code == 200

    def test_revenue_report_schema_fields(self):
        resp = client.get("/api/v1/report/revenue")
        data = resp.json()
        required_fields = [
            "period", "generated_at", "total_revenue", "recurring_revenue",
            "one_time_revenue", "revenue_by_month", "revenue_by_product",
            "projected_next_month", "collection_rate_percent",
            "outstanding_receivables", "ai_analysis", "risk_factors"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_revenue_report_risk_factors_is_list(self):
        resp = client.get("/api/v1/report/revenue")
        assert isinstance(resp.json()["risk_factors"], list)

    def test_revenue_report_projected_next_month_positive(self):
        resp = client.get("/api/v1/report/revenue")
        assert resp.json()["projected_next_month"] > 0

    def test_revenue_report_collection_rate_range(self):
        resp = client.get("/api/v1/report/revenue")
        rate = resp.json()["collection_rate_percent"]
        assert 0 <= rate <= 100


# ─────────────────────────────────────────────────────────────────────────────
class TestExpenseReport:
    def test_expense_report_returns_200(self):
        resp = client.get("/api/v1/report/expenses")
        assert resp.status_code == 200

    def test_expense_report_schema_fields(self):
        resp = client.get("/api/v1/report/expenses")
        data = resp.json()
        required_fields = [
            "period", "generated_at", "total_expenses", "expenses_by_category",
            "expenses_by_month", "operating_expenses", "non_operating_expenses",
            "expense_ratio_percent", "month_over_month_change_percent",
            "ai_insights", "cost_saving_opportunities"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_expense_report_categories_sum(self):
        resp = client.get("/api/v1/report/expenses")
        data = resp.json()
        category_total = sum(data["expenses_by_category"].values())
        # Should be approximately equal to total (within 1% due to rounding)
        assert abs(category_total - data["total_expenses"]) < data["total_expenses"] * 0.01

    def test_expense_report_cost_saving_is_list(self):
        resp = client.get("/api/v1/report/expenses")
        assert isinstance(resp.json()["cost_saving_opportunities"], list)

    def test_expense_report_expense_ratio_range(self):
        resp = client.get("/api/v1/report/expenses")
        ratio = resp.json()["expense_ratio_percent"]
        assert 0 <= ratio <= 100


# ─────────────────────────────────────────────────────────────────────────────
class TestCustomerAnalytics:
    def test_customer_analytics_returns_200(self):
        resp = client.get("/api/v1/report/customers")
        assert resp.status_code == 200

    def test_customer_analytics_schema_fields(self):
        resp = client.get("/api/v1/report/customers")
        data = resp.json()
        required_fields = [
            "period", "generated_at", "total_customers", "active_customers",
            "new_customers", "churned_customers", "churn_rate_percent",
            "customer_lifetime_value", "customer_acquisition_cost",
            "customers_by_segment", "customers_by_region", "top_customers",
            "ai_insights", "growth_recommendations"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_customer_analytics_growth_recommendations_is_list(self):
        resp = client.get("/api/v1/report/customers")
        assert isinstance(resp.json()["growth_recommendations"], list)

    def test_customer_analytics_churn_rate_range(self):
        resp = client.get("/api/v1/report/customers")
        churn = resp.json()["churn_rate_percent"]
        assert 0 <= churn <= 100

    def test_customer_analytics_active_less_than_total(self):
        resp = client.get("/api/v1/report/customers")
        data = resp.json()
        assert data["active_customers"] <= data["total_customers"]

    def test_customer_analytics_top_customers_is_list(self):
        resp = client.get("/api/v1/report/customers")
        assert isinstance(resp.json()["top_customers"], list)


# ─────────────────────────────────────────────────────────────────────────────
class TestRevenueForecast:
    def test_forecast_returns_200(self):
        resp = client.get("/api/v1/report/forecast")
        assert resp.status_code == 200

    def test_forecast_schema_fields(self):
        resp = client.get("/api/v1/report/forecast")
        data = resp.json()
        required_fields = [
            "period", "generated_at", "forecast_months", "total_forecasted_revenue",
            "confidence_percent", "forecast_method", "key_assumptions",
            "upside_scenario", "downside_scenario", "ai_analysis", "recommendations"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_forecast_recommendations_is_list(self):
        resp = client.get("/api/v1/report/forecast")
        assert isinstance(resp.json()["recommendations"], list)

    def test_forecast_key_assumptions_is_list(self):
        resp = client.get("/api/v1/report/forecast")
        assert isinstance(resp.json()["key_assumptions"], list)

    def test_forecast_confidence_in_range(self):
        resp = client.get("/api/v1/report/forecast")
        confidence = resp.json()["confidence_percent"]
        assert 0 <= confidence <= 100

    def test_forecast_upside_greater_than_base(self):
        resp = client.get("/api/v1/report/forecast")
        data = resp.json()
        assert data["upside_scenario"] >= data["total_forecasted_revenue"]

    def test_forecast_downside_less_than_base(self):
        resp = client.get("/api/v1/report/forecast")
        data = resp.json()
        assert data["downside_scenario"] <= data["total_forecasted_revenue"]

    def test_forecast_custom_period(self):
        resp = client.get("/api/v1/report/forecast?period=next_month")
        assert resp.status_code == 200
        assert resp.json()["period"] == "next_month"

    def test_forecast_has_monthly_breakdown(self):
        resp = client.get("/api/v1/report/forecast")
        data = resp.json()
        assert len(data["forecast_months"]) >= 1
        for month in data["forecast_months"]:
            assert "month" in month
            assert "forecast" in month