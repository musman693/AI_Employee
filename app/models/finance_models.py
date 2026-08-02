from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionCategory(str, Enum):
    SALARY = "salary"
    UTILITIES = "utilities"
    MARKETING = "marketing"
    RENT = "rent"
    SALES = "sales"
    REFUND = "refund"
    MISCELLANEOUS = "miscellaneous"


class FinanceSummaryResponse(BaseModel):
    period: str
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin_percent: float
    outstanding_invoices: int
    overdue_invoices: int
    ai_insight: str


class ForecastResponse(BaseModel):
    period: str
    projected_revenue: float
    projected_expenses: float
    projected_profit: float
    confidence_percent: float
    ai_analysis: str
    recommendations: List[str]


class AccountantReportResponse(BaseModel):
    report_id: str
    generated_at: str
    period: str
    income_summary: dict
    expense_summary: dict
    net_position: float
    tax_liability_estimate: float
    ai_notes: str


class CategorizeTransactionRequest(BaseModel):
    description: str
    amount: float
    transaction_type: Optional[TransactionType] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "description": "Monthly rent payment for office space",
            "amount": 85000,
            "transaction_type": "expense"
        }
    })


class CategorizeTransactionResponse(BaseModel):
    description: str
    amount: float
    suggested_category: TransactionCategory
    transaction_type: TransactionType
    confidence_percent: float
    ai_reasoning: str
