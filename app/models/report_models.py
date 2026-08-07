"""
report_models.py — Pydantic models for AI Reporting.

Models:
  - ReportPeriod: current_month, last_month, ytd, custom
  - SalesAnalyticsResponse: Sales analytics with trends and breakdowns
  - RevenueReportResponse: Revenue report with projections
  - ExpenseReportResponse: Expense report with category breakdown
  - CustomerAnalyticsResponse: Customer analytics with segmentation
  - ForecastResponse: Revenue forecasting with AI analysis
"""

from datetime import date
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any


class ReportPeriod(str, Enum):
    CURRENT_MONTH = "current_month"
    LAST_MONTH = "last_month"
    CURRENT_QUARTER = "current_quarter"
    LAST_QUARTER = "last_quarter"
    YTD = "ytd"
    CUSTOM = "custom"


class SalesAnalyticsResponse(BaseModel):
    """Sales analytics with trends and breakdowns."""
    period: str
    generated_at: str
    total_sales: float
    total_orders: int
    average_order_value: float
    sales_by_month: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    sales_by_channel: Dict[str, float]
    conversion_rate_percent: float
    growth_rate_percent: Optional[float]
    ai_insights: str
    recommendations: List[str]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "current_month",
            "generated_at": "2026-08-07T23:00:00",
            "total_sales": 1250000.0,
            "total_orders": 45,
            "average_order_value": 27777.78,
            "sales_by_month": [
                {"month": "June", "sales": 980000},
                {"month": "July", "sales": 1150000},
                {"month": "August", "sales": 1250000}
            ],
            "top_products": [
                {"product": "AI Email Assistant", "revenue": 450000, "units": 15},
                {"product": "CRM Module", "revenue": 380000, "units": 12}
            ],
            "sales_by_channel": {
                "direct": 750000,
                "referral": 350000,
                "partner": 150000
            },
            "conversion_rate_percent": 24.5,
            "growth_rate_percent": 12.3,
            "ai_insights": "Sales are trending upward with a 12.3% growth rate.",
            "recommendations": [
                "Focus on referral channel — highest conversion rate.",
                "Consider expanding partner network for Q4."
            ]
        }
    })


class RevenueReportResponse(BaseModel):
    """Revenue report with projections."""
    period: str
    generated_at: str
    total_revenue: float
    recurring_revenue: float
    one_time_revenue: float
    revenue_by_month: List[Dict[str, Any]]
    revenue_by_product: Dict[str, float]
    projected_next_month: float
    collection_rate_percent: float
    outstanding_receivables: float
    ai_analysis: str
    risk_factors: List[str]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "current_month",
            "generated_at": "2026-08-07T23:00:00",
            "total_revenue": 980000.0,
            "recurring_revenue": 650000.0,
            "one_time_revenue": 330000.0,
            "revenue_by_month": [
                {"month": "June", "revenue": 820000},
                {"month": "July", "revenue": 920000},
                {"month": "August", "revenue": 980000}
            ],
            "revenue_by_product": {
                "AI Email Assistant": 350000,
                "CRM Module": 280000,
                "Invoice Generator": 200000,
                "Other": 150000
            },
            "projected_next_month": 1120000.0,
            "collection_rate_percent": 87.5,
            "outstanding_receivables": 145000.0,
            "ai_analysis": "Revenue is healthy with strong recurring base.",
            "risk_factors": [
                "Outstanding receivables at 12.5% — monitor collections.",
                "One-time revenue declined 15% MoM."
            ]
        }
    })


class ExpenseReportResponse(BaseModel):
    """Expense report with category breakdown."""
    period: str
    generated_at: str
    total_expenses: float
    expenses_by_category: Dict[str, float]
    expenses_by_month: List[Dict[str, Any]]
    operating_expenses: float
    non_operating_expenses: float
    expense_ratio_percent: float
    month_over_month_change_percent: float
    ai_insights: str
    cost_saving_opportunities: List[str]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "current_month",
            "generated_at": "2026-08-07T23:00:00",
            "total_expenses": 420000.0,
            "expenses_by_category": {
                "salaries": 250000,
                "infrastructure": 80000,
                "marketing": 45000,
                "office": 25000,
                "other": 20000
            },
            "expenses_by_month": [
                {"month": "June", "expenses": 380000},
                {"month": "July", "expenses": 400000},
                {"month": "August", "expenses": 420000}
            ],
            "operating_expenses": 395000.0,
            "non_operating_expenses": 25000.0,
            "expense_ratio_percent": 42.9,
            "month_over_month_change_percent": 5.0,
            "ai_insights": "Expenses are within budget at 42.9% of revenue.",
            "cost_saving_opportunities": [
                "Review cloud infrastructure — 19% of expenses.",
                "Consider annual billing for SaaS tools — potential 15% savings."
            ]
        }
    })


class CustomerAnalyticsResponse(BaseModel):
    """Customer analytics with segmentation."""
    period: str
    generated_at: str
    total_customers: int
    active_customers: int
    new_customers: int
    churned_customers: int
    churn_rate_percent: float
    customer_lifetime_value: float
    customer_acquisition_cost: float
    customers_by_segment: Dict[str, int]
    customers_by_region: Dict[str, int]
    top_customers: List[Dict[str, Any]]
    ai_insights: str
    growth_recommendations: List[str]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "current_month",
            "generated_at": "2026-08-07T23:00:00",
            "total_customers": 156,
            "active_customers": 142,
            "new_customers": 18,
            "churned_customers": 4,
            "churn_rate_percent": 2.6,
            "customer_lifetime_value": 285000.0,
            "customer_acquisition_cost": 12500.0,
            "customers_by_segment": {
                "enterprise": 12,
                "small_business": 89,
                "startup": 55
            },
            "customers_by_region": {
                "North America": 65,
                "Europe": 48,
                "Asia Pacific": 32,
                "Other": 11
            },
            "top_customers": [
                {"name": "TechCorp Inc", "revenue": 450000, "projects": 8},
                {"name": "StartupXYZ", "revenue": 320000, "projects": 5}
            ],
            "ai_insights": "Customer base is healthy with 2.6% churn rate.",
            "growth_recommendations": [
                "Focus on enterprise segment — highest LTV.",
                "Asia Pacific shows fastest growth — consider local expansion."
            ]
        }
    })


class RevenueForecastResponse(BaseModel):
    """Revenue forecasting with AI analysis."""
    period: str
    generated_at: str
    forecast_months: List[Dict[str, Any]]
    total_forecasted_revenue: float
    confidence_percent: float
    forecast_method: str
    key_assumptions: List[str]
    upside_scenario: float
    downside_scenario: float
    ai_analysis: str
    recommendations: List[str]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "next_quarter",
            "generated_at": "2026-08-07T23:00:00",
            "forecast_months": [
                {"month": "September", "forecast": 1120000},
                {"month": "October", "forecast": 1250000},
                {"month": "November", "forecast": 1380000}
            ],
            "total_forecasted_revenue": 3750000.0,
            "confidence_percent": 78.5,
            "forecast_method": "time_series_with_pipeline_analysis",
            "key_assumptions": [
                "Current pipeline converts at historical 24% rate.",
                "No major customer churn expected.",
                "Seasonal Q4 uplift of 15% applied."
            ],
            "upside_scenario": 4200000.0,
            "downside_scenario": 3100000.0,
            "ai_analysis": "Q4 forecast shows strong growth trajectory.",
            "recommendations": [
                "Accelerate pipeline deals to capture Q4 forecast.",
                "Hire 2 additional AEs to handle pipeline volume.",
                "Launch enterprise campaign in September."
            ]
        }
    })


class ReportRequest(BaseModel):
    """Request model for generating reports with custom parameters."""
    period: ReportPeriod = ReportPeriod.CURRENT_MONTH
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format (for custom period)")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format (for custom period)")
    include_projections: bool = True
    granularity: str = Field("monthly", description="monthly, weekly, daily")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "custom",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "include_projections": True,
            "granularity": "monthly"
        }
    })