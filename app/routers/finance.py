"""
finance.py — AI Finance Assistant & AI Accountant API endpoints.

Endpoints:
  GET   /api/v1/finance/summary                  AI Finance Assistant: revenue/expense summary
  GET   /api/v1/finance/forecast                 AI-generated cash flow forecast
  GET   /api/v1/finance/accountant/report        AI Accountant: accounting report
  POST  /api/v1/finance/accountant/categorize    Categorize a transaction using AI

Note: AI responses are currently structured mock outputs with realistic data.
      To enable real OpenAI calls, set OPENAI_API_KEY in .env and uncomment
      the openai block at the bottom of each endpoint.
"""

from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

from app.models.finance_models import (
    FinanceSummaryResponse, ForecastResponse,
    AccountantReportResponse, CategorizeTransactionRequest,
    CategorizeTransactionResponse, TransactionCategory, TransactionType,
)

# Optional: uncomment to enable live OpenAI calls
# import openai, os
# openai.api_key = os.getenv("OPENAI_API_KEY", "")

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# GET /summary
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/summary", response_model=FinanceSummaryResponse,
            summary="AI Finance Assistant — revenue & expense summary")
def get_finance_summary(
    period: Optional[str] = Query("current_month", description="Period: current_month | last_month | ytd"),
):
    """
    Returns a financial summary for the requested period, including:
    - Total revenue and expenses
    - Net profit and margin
    - Outstanding and overdue invoice counts
    - An AI-generated insight comment

    AI Insight is currently a structured mock. Connect to OpenAI GPT for live analysis.
    """

    # ── Pull real data from invoice store if available ────────────────────────
    # (In production, query PostgreSQL here)
    from app.routers.invoice import _invoices
    from app.models.invoice_models import InvoiceStatus
    from datetime import date

    total_revenue   = 0.0
    outstanding_cnt = 0
    overdue_cnt     = 0
    for inv in _invoices.values():
        if inv["status"] == InvoiceStatus.PAID:
            total_revenue += inv["total"]
        elif inv["status"] in (InvoiceStatus.SENT, InvoiceStatus.DRAFT):
            outstanding_cnt += 1
            due = inv.get("due_date")
            if due:
                d = date.fromisoformat(str(due)) if isinstance(due, str) else due
                if d < date.today():
                    overdue_cnt += 1

    # Estimated expenses — mock (in production: pull from expense DB)
    total_expenses     = round(total_revenue * 0.42, 2)
    net_profit         = round(total_revenue - total_expenses, 2)
    profit_margin_pct  = round((net_profit / total_revenue * 100) if total_revenue else 0, 2)

    ai_insight = (
        f"Your net profit margin is {profit_margin_pct:.1f}% for the {period.replace('_', ' ')}. "
        f"You have {outstanding_cnt} outstanding and {overdue_cnt} overdue invoices. "
        "Consider sending reminders to overdue clients to improve cash flow."
        if total_revenue > 0
        else
        "No paid invoices recorded yet. Create and mark invoices as paid to see your financial summary."
    )

    return FinanceSummaryResponse(
        period=period,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        profit_margin_percent=profit_margin_pct,
        outstanding_invoices=outstanding_cnt,
        overdue_invoices=overdue_cnt,
        ai_insight=ai_insight,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /forecast
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/forecast", response_model=ForecastResponse,
            summary="AI Finance Assistant — cash flow forecast")
def get_finance_forecast(
    period: Optional[str] = Query("next_month", description="Forecast period: next_month | next_quarter"),
):
    """
    Returns an AI-generated cash flow forecast.
    Currently returns a structured mock response. Plug in OpenAI GPT for live forecasting.
    """
    from app.routers.invoice import _invoices
    from app.models.invoice_models import InvoiceStatus

    paid_total = sum(inv["total"] for inv in _invoices.values() if inv["status"] == InvoiceStatus.PAID)

    projected_revenue  = round(paid_total * 1.15, 2)   # +15% growth assumption
    projected_expenses = round(projected_revenue * 0.40, 2)
    projected_profit   = round(projected_revenue - projected_expenses, 2)

    return ForecastResponse(
        period=period,
        projected_revenue=projected_revenue,
        projected_expenses=projected_expenses,
        projected_profit=projected_profit,
        confidence_percent=72.5,
        ai_analysis=(
            f"Based on current invoice data, revenue is projected to grow by 15% "
            f"in the {period.replace('_', ' ')}. Expenses are estimated at 40% of revenue. "
            "Maintaining timely invoice collection will be key to achieving this target."
        ),
        recommendations=[
            "Follow up on all overdue invoices within 48 hours.",
            "Review recurring subscription invoices for upsell opportunities.",
            "Keep operating expenses below 40% of projected revenue.",
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /accountant/report
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/accountant/report", response_model=AccountantReportResponse,
            summary="AI Accountant — generate accounting report")
def get_accountant_report(
    period: Optional[str] = Query("current_month", description="Period: current_month | last_month | ytd"),
):
    """
    Generates a structured accounting report for the requested period.
    Includes income summary, expense breakdown, net position, and estimated tax liability.
    """
    from app.routers.invoice import _invoices
    from app.models.invoice_models import InvoiceStatus

    total_revenue = sum(inv["total"] for inv in _invoices.values() if inv["status"] == InvoiceStatus.PAID)
    total_expenses = round(total_revenue * 0.42, 2)
    net_position   = round(total_revenue - total_expenses, 2)
    tax_liability  = round(net_position * 0.17, 2)   # 17% GST estimate

    return AccountantReportResponse(
        report_id=f"RPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        generated_at=datetime.utcnow().isoformat(),
        period=period,
        income_summary={
            "total_invoiced":  total_revenue,
            "source_invoices": sum(1 for i in _invoices.values() if i["status"] == InvoiceStatus.PAID),
        },
        expense_summary={
            "estimated_total": total_expenses,
            "note": "Expense data pulled from mock estimates. Connect expense DB for accurate figures.",
        },
        net_position=net_position,
        tax_liability_estimate=tax_liability,
        ai_notes=(
            f"Net position for {period.replace('_', ' ')}: PKR {net_position:,.2f}. "
            f"Estimated GST liability (17%): PKR {tax_liability:,.2f}. "
            "Ensure all expenses are logged before filing taxes."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /accountant/categorize
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/accountant/categorize", response_model=CategorizeTransactionResponse,
             summary="AI Accountant — categorize a transaction")
def categorize_transaction(payload: CategorizeTransactionRequest):
    """
    Uses AI to suggest a category for a financial transaction based on its description.
    Currently uses keyword-based rule logic as a mock.
    Set OPENAI_API_KEY in .env and uncomment the openai block below for live GPT categorization.
    """

    # ── Keyword-based mock categorization ────────────────────────────────────
    desc_lower = payload.description.lower()

    category_rules = [
        (TransactionCategory.SALARY,       ["salary", "payroll", "wages", "staff", "employee"]),
        (TransactionCategory.UTILITIES,    ["electricity", "gas", "water", "internet", "utility", "bill"]),
        (TransactionCategory.MARKETING,    ["ads", "advertisement", "campaign", "marketing", "social media", "seo"]),
        (TransactionCategory.RENT,         ["rent", "lease", "office", "property"]),
        (TransactionCategory.SALES,        ["sale", "invoice", "revenue", "client payment", "received"]),
        (TransactionCategory.REFUND,       ["refund", "return", "chargeback", "reversal"]),
    ]

    suggested_category = TransactionCategory.MISCELLANEOUS
    confidence         = 60.0

    for category, keywords in category_rules:
        if any(kw in desc_lower for kw in keywords):
            suggested_category = category
            confidence = 88.0
            break

    # Determine transaction type
    tx_type = payload.transaction_type
    if tx_type is None:
        tx_type = TransactionType.INCOME if suggested_category == TransactionCategory.SALES else TransactionType.EXPENSE

    reasoning_map = {
        TransactionCategory.SALARY:        "Description mentions staff or payroll-related terms.",
        TransactionCategory.UTILITIES:     "Description references utility services like electricity, internet, or gas.",
        TransactionCategory.MARKETING:     "Description contains marketing or advertising keywords.",
        TransactionCategory.RENT:          "Description includes rent or lease-related terms.",
        TransactionCategory.SALES:         "Description indicates a sale or client payment.",
        TransactionCategory.REFUND:        "Description mentions a refund, return, or chargeback.",
        TransactionCategory.MISCELLANEOUS: "No specific category keywords matched. Classified as miscellaneous.",
    }

    # ── Live OpenAI alternative (uncomment to use) ────────────────────────────
    # response = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{
    #         "role": "system",
    #         "content": "You are a financial accounting assistant. Categorize the transaction."
    #     }, {
    #         "role": "user",
    #         "content": f"Transaction: {payload.description}, Amount: {payload.amount}"
    #     }]
    # )
    # suggested_category = response.choices[0].message.content  # parse accordingly

    return CategorizeTransactionResponse(
        description=payload.description,
        amount=payload.amount,
        suggested_category=suggested_category,
        transaction_type=tx_type,
        confidence_percent=confidence,
        ai_reasoning=reasoning_map[suggested_category],
    )
