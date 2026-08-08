from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import date


class QuotationStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    discount_percent: Optional[float] = 0.0

    @property
    def total(self) -> float:
        subtotal = self.quantity * self.unit_price
        return subtotal * (1 - self.discount_percent / 100)


class CompanyBranding(BaseModel):
    company_name: str
    address: str
    phone: str
    email: str
    logo_url: Optional[str] = None
    website: Optional[str] = None


class CreateQuotationRequest(BaseModel):
    branding: CompanyBranding
    client_name: str
    client_email: str
    client_address: Optional[str] = None
    line_items: List[LineItem]
    tax_percent: Optional[float] = 0.0
    global_discount_percent: Optional[float] = 0.0
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = "Net 30"

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "branding": {
                "company_name": "Acme Corp",
                "address": "123 Main St, Karachi",
                "phone": "+92-300-1234567",
                "email": "billing@acmecorp.com"
            },
            "client_name": "Beta Ltd",
            "client_email": "client@betaltd.com",
            "line_items": [
                {"description": "Web Development", "quantity": 1, "unit_price": 150000, "discount_percent": 10}
            ],
            "tax_percent": 17,
            "valid_until": "2026-09-01",
            "notes": "Payment due within 30 days."
        }
    })


class QuotationResponse(BaseModel):
    id: str
    status: QuotationStatus
    branding: CompanyBranding
    client_name: str
    client_email: str
    client_address: Optional[str]
    line_items: List[LineItem]
    tax_percent: float
    global_discount_percent: float
    subtotal: float
    discount_amount: float
    tax_amount: float
    total: float
    valid_until: Optional[date]
    notes: Optional[str]
    payment_terms: str
    created_at: str


class ApproveRejectResponse(BaseModel):
    id: str
    status: QuotationStatus
    message: str


class SendEmailRequest(BaseModel):
    recipient_email: Optional[str] = None  # defaults to client_email
    subject: Optional[str] = None
    body: Optional[str] = None


class SendEmailResponse(BaseModel):
    id: str
    message: str
    recipient_email: str
