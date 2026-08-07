"""
report.py — AI Reporting API endpoints.

Endpoints:
  GET /api/v1/report/sales              Sales analytics with trends and breakdowns
  GET /api/v1/report/revenue            Revenue report with projections
  GET /api/v1/report/expenses           Expense report with category breakdown
  GET /api/v1/report/customers          Customer analytics with segmentation
  GET /api/v1/report/forecast           Revenue forecasting with AI analysis

Note: Reports currently use mock data aggregated from other modules (invoice, finance).
      Connect to PostgreSQL and analytics DB for production reporting.
      AI insights are structured mocks; uncomment OpenAI blocks for live analysis.
"""

from datetime import datetime, date, timedelta
from fastapi import APIRouter, Query
from typing import Optional, List, Dict
import random

from app.models.report_models import (
    SalesAnalyticsResponse, RevenueReportResponse,
    ExpenseReportResponse, CustomerAnalyticsResponse,
    RevenueForecastResponse, ReportPeriod,
)

router = APIRouter()


def _get_period_label(period: str) -> str:
    """Get a human-readable label for the period."""
    return period.replace("_", " ").title()


def _generate_ai_insight(data: dict, report_type: str) -> str:
    """Generate AI-powered insights (mock implementation)."""
    # Uncomment below for live OpenAI integration:
    # import openai, os
    # openai.api_key = os.getenv("OPENAI_API_KEY", "")
    # response = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{
    #         "role": "system",
    #         "content": f"You are a business analytics AI. Generate insights for {report_type}."
    #     }, {
    #         "role": "user",
    #         "content": f"Data: {data}"
    #     }]
    # )
    # return response.choices[0].message.content

    if report_type == "sales":
        growth = data.get("growth_rate_percent", 0)
        if growth > 10:
            return f"Strong sales growth of {growth:.1f}% — consider scaling sales team and marketing spend."
        elif growth > 0:
            return f"Moderate growth of {growth:.1f}% — focus on conversion optimization to accelerate."
        else:
            return "Sales are declining — immediate action needed on pipeline and pricing strategy."
    elif report_type == "revenue":
        ratio = data.get("expense_ratio_percent", 50)
        if ratio < 40:
            return f"Healthy expense ratio of {ratio:.1f}% — room to invest in growth initiatives."
        elif ratio < 60:
            return f"Expense ratio at {ratio:.1f}% — monitor closely and optimize operational efficiency."
        else:
            return f"High expense ratio of {ratio:.1f}% — urgent cost optimization required."
    elif report_type == "customer":
        churn = data.get("churn_rate_percent", 5)
        if churn < 3:
            return f"Excellent churn rate of {churn:.1f}% — focus on upselling to existing customers."
        elif churn < 5:
            return f"Acceptable churn at {churn:.1f}% — investigate at-risk accounts."
        else:
            return f"High churn rate of {churn:.1f}% — prioritize customer success and product improvements."
    return "Review the detailed metrics for actionable insights."


# ─────────────────────────────────────────────────────────────────────────────
# GET /sales — Sales analytics
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/sales", response_model=SalesAnalyticsResponse,
            summary="AI Reporting — sales analytics")
def get_sales_analytics(
    period: str = Query("current_month", description="Report period"),
):
    """
    Returns comprehensive sales analytics including total sales, order counts,
    trends, top products, channel breakdown, and AI-generated insights.
    """
    # Pull real data from invoice store if available
    total_sales = 0.0
    total_orders = 0
    try:
        from app.routers.invoice import _invoices
        from app.models.invoice_models import InvoiceStatus

        paid_invoices = [inv for inv in _invoices.values() if inv["status"] == InvoiceStatus.PAID]
        total_sales = sum(inv["total"] for inv in paid_invoices)
        total_orders = len(paid_invoices)
    except (ImportError, Exception):
        pass

    # Use mock data if no real data available
    if total_sales == 0:
        total_sales = random.uniform(800000, 1500000)
        total_orders = random.randint(30, 60)

    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    growth_rate = random.uniform(5, 18)

    data = {
        "growth_rate_percent": growth_rate,
        "total_sales": total_sales,
        "conversion_rate_percent": random.uniform(20, 30),
    }

    return SalesAnalyticsResponse(
        period=period,
        generated_at=datetime.utcnow().isoformat(),
        total_sales=round(total_sales, 2),
        total_orders=total_orders,
        average_order_value=round(avg_order_value, 2),
        sales_by_month=[
            {"month": "June", "sales": round(total_sales * 0.85, 2)},
            {"month": "July", "sales": round(total_sales * 0.92, 2)},
            {"month": "August", "sales": round(total_sales, 2)},
        ],
        top_products=[
            {"product": "AI Email Assistant", "revenue": round(total_sales * 0.35, 2), "units": max(1, int(total_orders * 0.3))},
            {"product": "CRM Module", "revenue": round(total_sales * 0.28, 2), "units": max(1, int(total_orders * 0.25))},
            {"product": "Invoice Generator", "revenue": round(total_sales * 0.22, 2), "units": max(1, int(total_orders * 0.2))},
        ],
        sales_by_channel={
            "direct": round(total_sales * 0.55, 2),
            "referral": round(total_sales * 0.30, 2),
            "partner": round(total_sales * 0.15, 2),
        },
        conversion_rate_percent=round(random.uniform(22, 28), 1),
        growth_rate_percent=round(growth_rate, 1),
        ai_insights=_generate_ai_insight(data, "sales"),
        recommendations=[
            "Focus on referral channel — highest conversion rate.",
            "Consider expanding partner network for Q4.",
            "Launch targeted campaign for top-performing products.",
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /revenue — Revenue report
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/revenue", response_model=RevenueReportResponse,
            summary="AI Reporting — revenue report with projections")
def get_revenue_report(
    period: str = Query("current_month", description="Report period"),
):
    """
    Returns a comprehensive revenue report including recurring vs one-time revenue,
    monthly trends, product breakdown, projections, and risk factors.
    """
    # Pull real data from invoice store if available
    total_revenue = 0.0
    outstanding = 0.0
    try:
        from app.routers.invoice import _invoices
        from app.models.invoice_models import InvoiceStatus

        paid_invoices = [inv for inv in _invoices.values() if inv["status"] == InvoiceStatus.PAID]
        sent_invoices = [inv for inv in _invoices.values() if inv["status"] == InvoiceStatus.SENT]

        total_revenue = sum(inv["total"] for inv in paid_invoices)
        outstanding = sum(inv["total"] for inv in sent_invoices)
    except (ImportError, Exception):
        pass

    # Use mock data if no real data available
    if total_revenue == 0:
        total_revenue = random.uniform(700000, 1200000)
        outstanding = random.uniform(50000, 200000)

    recurring_pct = random.uniform(0.60, 0.75)
    recurring_revenue = total_revenue * recurring_pct
    one_time_revenue = total_revenue - recurring_revenue
    collection_rate = random.uniform(82, 92)

    data = {"expense_ratio_percent": random.uniform(38, 48)}

    # Avoid division by zero
    total_for_pct = max(total_revenue + outstanding, 1)

    return RevenueReportResponse(
        period=period,
        generated_at=datetime.utcnow().isoformat(),
        total_revenue=round(total_revenue, 2),
        recurring_revenue=round(recurring_revenue, 2),
        one_time_revenue=round(one_time_revenue, 2),
        revenue_by_month=[
            {"month": "June", "revenue": round(total_revenue * 0.85, 2)},
            {"month": "July", "revenue": round(total_revenue * 0.93, 2)},
            {"month": "August", "revenue": round(total_revenue, 2)},
        ],
        revenue_by_product={
            "AI Email Assistant": round(total_revenue * 0.35, 2),
            "CRM Module": round(total_revenue * 0.28, 2),
            "Invoice Generator": round(total_revenue * 0.22, 2),
            "Other": round(total_revenue * 0.15, 2),
        },
        projected_next_month=round(total_revenue * random.uniform(1.08, 1.18), 2),
        collection_rate_percent=round(collection_rate, 1),
        outstanding_receivables=round(outstanding, 2),
        ai_analysis=_generate_ai_insight(data, "revenue"),
        risk_factors=[
            f"Outstanding receivables at {round(outstanding / total_for_pct * 100, 1)}% — monitor collections.",
            "One-time revenue volatility — strengthen recurring revenue base.",
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /expenses — Expense report
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/expenses", response_model=ExpenseReportResponse,
            summary="AI Reporting — expense report with category breakdown")
def get_expense_report(
    period: str = Query("current_month", description="Report period"),
):
    """
    Returns a detailed expense report with category breakdown, monthly trends,
    operating vs non-operating expenses, and cost-saving recommendations.
    """
    # Pull revenue data to calculate expense ratio
    total_revenue = 0.0
    try:
        from app.routers.invoice import _invoices
        from app.models.invoice_models import InvoiceStatus
        total_revenue = sum(inv["total"] for inv in _invoices.values() if inv["status"] == InvoiceStatus.PAID)
    except (ImportError, Exception):
        pass

    # Use mock data if no real data available
    if total_revenue == 0:
        total_revenue = random.uniform(800000, 1200000)

    total_expenses = total_revenue * random.uniform(0.38, 0.48)
    operating_expenses = total_expenses * random.uniform(0.90, 0.95)
    non_operating = total_expenses - operating_expenses
    mom_change = random.uniform(-3, 8)

    # Avoid division by zero
    expense_ratio = round(total_expenses / max(total_revenue, 1) * 100, 1)
    data = {"expense_ratio_percent": expense_ratio}

    return ExpenseReportResponse(
        period=period,
        generated_at=datetime.utcnow().isoformat(),
        total_expenses=round(total_expenses, 2),
        expenses_by_category={
            "salaries": round(total_expenses * 0.55, 2),
            "infrastructure": round(total_expenses * 0.18, 2),
            "marketing": round(total_expenses * 0.12, 2),
            "office": round(total_expenses * 0.08, 2),
            "other": round(total_expenses * 0.07, 2),
        },
        expenses_by_month=[
            {"month": "June", "expenses": round(total_expenses * 0.92, 2)},
            {"month": "July", "expenses": round(total_expenses * 0.96, 2)},
            {"month": "August", "expenses": round(total_expenses, 2)},
        ],
        operating_expenses=round(operating_expenses, 2),
        non_operating_expenses=round(non_operating, 2),
        expense_ratio_percent=expense_ratio,
        month_over_month_change_percent=round(mom_change, 1),
        ai_insights=_generate_ai_insight(data, "expenses"),
        cost_saving_opportunities=[
            "Review cloud infrastructure — 18% of expenses.",
            "Consider annual billing for SaaS tools — potential 15% savings.",
            "Optimize marketing spend — focus on highest ROI channels.",
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /customers — Customer analytics
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/customers", response_model=CustomerAnalyticsResponse,
            summary="AI Reporting — customer analytics with segmentation")
def get_customer_analytics(
    period: str = Query("current_month", description="Report period"),
):
    """
    Returns customer analytics including total/active/new/churned customers,
    segmentation, regional distribution, top customers, and growth recommendations.
    """
    total_customers = random.randint(120, 200)
    active_pct = random.uniform(0.88, 0.95)
    active_customers = int(total_customers * active_pct)
    new_customers = random.randint(10, 25)
    churned_customers = random.randint(2, 6)
    churn_rate = (churned_customers / total_customers) * 100
    clv = random.uniform(200000, 400000)
    cac = random.uniform(8000, 18000)

    data = {"churn_rate_percent": churn_rate}

    return CustomerAnalyticsResponse(
        period=period,
        generated_at=datetime.utcnow().isoformat(),
        total_customers=total_customers,
        active_customers=active_customers,
        new_customers=new_customers,
        churned_customers=churned_customers,
        churn_rate_percent=round(churn_rate, 1),
        customer_lifetime_value=round(clv, 2),
        customer_acquisition_cost=round(cac, 2),
        customers_by_segment={
            "enterprise": random.randint(8, 18),
            "small_business": random.randint(60, 100),
            "startup": random.randint(40, 70),
        },
        customers_by_region={
            "North America": int(total_customers * 0.40),
            "Europe": int(total_customers * 0.32),
            "Asia Pacific": int(total_customers * 0.20),
            "Other": total_customers - int(total_customers * 0.92),
        },
        top_customers=[
            {"name": "TechCorp Inc", "revenue": round(clv * random.uniform(1.5, 2.5), 0), "projects": random.randint(5, 12)},
            {"name": "StartupXYZ", "revenue": round(clv * random.uniform(1.2, 2.0), 0), "projects": random.randint(3, 8)},
            {"name": "Enterprise Co", "revenue": round(clv * random.uniform(1.0, 1.8), 0), "projects": random.randint(2, 6)},
        ],
        ai_insights=_generate_ai_insight(data, "customer"),
        growth_recommendations=[
            "Focus on enterprise segment — highest LTV.",
            "Asia Pacific shows fastest growth — consider local expansion.",
            "Improve onboarding to reduce early-stage churn.",
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /forecast — Revenue forecasting
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/forecast", response_model=RevenueForecastResponse,
            summary="AI Reporting — revenue forecasting with AI analysis")
def get_revenue_forecast(
    period: str = Query("next_quarter", description="Forecast period: next_month | next_quarter"),
):
    """
    Returns an AI-generated revenue forecast with monthly breakdowns,
    confidence levels, scenarios, and strategic recommendations.
    """
    # Pull current revenue data
    current_revenue = 0.0
    try:
        from app.routers.invoice import _invoices
        from app.models.invoice_models import InvoiceStatus
        current_revenue = sum(inv["total"] for inv in _invoices.values() if inv["status"] == InvoiceStatus.PAID)
    except (ImportError, Exception):
        pass

    # Use mock data if no real data available
    if current_revenue == 0:
        current_revenue = random.uniform(800000, 1200000)

    monthly_growth = random.uniform(0.08, 0.15)
    confidence = random.uniform(72, 85)

    months_ahead = 3 if period == "next_quarter" else 1
    forecast_months = []
    base = current_revenue

    # Full year of month names
    all_month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for i in range(1, months_ahead + 1):
        month_idx = (datetime.now().month - 1 + i) % 12
        forecast_val = round(base * (1 + monthly_growth) ** i, 2)
        forecast_months.append({
            "month": all_month_names[month_idx],
            "forecast": forecast_val,
        })

    total_forecast = sum(m["forecast"] for m in forecast_months)

    return RevenueForecastResponse(
        period=period,
        generated_at=datetime.utcnow().isoformat(),
        forecast_months=forecast_months,
        total_forecasted_revenue=round(total_forecast, 2),
        confidence_percent=round(confidence, 1),
        forecast_method="time_series_with_pipeline_analysis",
        key_assumptions=[
            "Current pipeline converts at historical 24% rate.",
            "No major customer churn expected.",
            f"Monthly growth rate of {monthly_growth*100:.1f}% projected.",
        ],
        upside_scenario=round(total_forecast * 1.15, 2),
        downside_scenario=round(total_forecast * 0.85, 2),
        ai_analysis=f"{'Q4' if months_ahead == 3 else 'Next month'} forecast shows {'strong' if monthly_growth > 0.1 else 'moderate'} growth trajectory.",
        recommendations=[
            "Accelerate pipeline deals to capture forecast.",
            "Monitor leading indicators weekly for early course correction.",
            "Consider strategic hires to support growth trajectory.",
        ],
    )