from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import date


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class RecurringFrequency(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class InvoiceLineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    discount_percent: Optional[float] = 0.0


class CreateInvoiceRequest(BaseModel):
    company_name: str
    company_address: str
    company_email: str
    company_phone: str
    client_name: str
    client_email: str
    client_address: Optional[str] = None
    line_items: List[InvoiceLineItem]
    tax_percent: Optional[float] = 0.0
    due_date: Optional[date] = None
    payment_link: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "company_name": "Acme Corp",
            "company_address": "123 Main St, Karachi",
            "company_email": "billing@acmecorp.com",
            "company_phone": "+92-300-1234567",
            "client_name": "Beta Ltd",
            "client_email": "client@betaltd.com",
            "line_items": [
                {"description": "SEO Services - July", "quantity": 1, "unit_price": 50000}
            ],
            "tax_percent": 17,
            "due_date": "2026-08-31",
            "payment_link": "https://pay.example.com/inv-001"
        }
    })


class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    status: InvoiceStatus
    company_name: str
    company_address: str
    company_email: str
    company_phone: str
    client_name: str
    client_email: str
    client_address: Optional[str]
    line_items: List[InvoiceLineItem]
    tax_percent: float
    subtotal: float
    tax_amount: float
    total: float
    due_date: Optional[date]
    payment_link: Optional[str]
    notes: Optional[str]
    qr_code_base64: Optional[str] = None
    created_at: str
    paid_at: Optional[str] = None


class MarkPaidResponse(BaseModel):
    id: str
    status: InvoiceStatus
    paid_at: str
    message: str


class ReminderResponse(BaseModel):
    id: str
    message: str
    client_email: str
    due_date: Optional[str]


class RecurringInvoiceRequest(BaseModel):
    base_invoice_id: str
    frequency: RecurringFrequency
    start_date: date
    end_date: Optional[date] = None
    auto_send: Optional[bool] = False

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "base_invoice_id": "inv-001",
            "frequency": "monthly",
            "start_date": "2026-09-01",
            "auto_send": False
        }
    })


class RecurringInvoiceResponse(BaseModel):
    recurring_id: str
    base_invoice_id: str
    frequency: RecurringFrequency
    start_date: date
    end_date: Optional[date]
    auto_send: bool
    message: str
