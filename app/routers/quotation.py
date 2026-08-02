"""
quotation.py — AI Quotation Generator API endpoints.

Endpoints:
  POST   /api/v1/quotation/create          Create a new quotation
  GET    /api/v1/quotation/list            List all quotations
  GET    /api/v1/quotation/{id}            Get a quotation by ID
  PUT    /api/v1/quotation/{id}/approve    Approve a quotation
  PUT    /api/v1/quotation/{id}/reject     Reject a quotation
  POST   /api/v1/quotation/{id}/send-email Email the quotation PDF to the client
  GET    /api/v1/quotation/{id}/pdf        Download the quotation as a PDF
"""

import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.models.quotation_models import (
    CreateQuotationRequest, QuotationResponse, QuotationStatus,
    ApproveRejectResponse, SendEmailRequest, SendEmailResponse,
)
from app.services.pdf_service import generate_quotation_pdf
from app.services.email_service import send_document_email

router = APIRouter()

# ── In-memory store (swap for PostgreSQL via Module 6 later) ─────────────────
_quotations: dict[str, dict] = {}


def _compute_totals(line_items, tax_percent, global_discount_percent):
    subtotal = 0.0
    for item in line_items:
        qty   = item.quantity
        price = item.unit_price
        disc  = item.discount_percent or 0.0
        subtotal += qty * price * (1 - disc / 100)
    discount_amount = subtotal * (global_discount_percent / 100)
    after_discount  = subtotal - discount_amount
    tax_amount      = after_discount * (tax_percent / 100)
    total           = after_discount + tax_amount
    return subtotal, discount_amount, tax_amount, total


def _to_response(q: dict) -> QuotationResponse:
    return QuotationResponse(**q)


# ─────────────────────────────────────────────────────────────────────────────
# POST /create
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/create", response_model=QuotationResponse, summary="Create a new quotation")
def create_quotation(payload: CreateQuotationRequest):
    """
    Create a new AI-powered quotation with company branding, line items,
    tax calculation, discounts, and payment terms.
    """
    q_id = f"QUO-{uuid.uuid4().hex[:8].upper()}"
    subtotal, discount_amount, tax_amount, total = _compute_totals(
        payload.line_items,
        payload.tax_percent or 0.0,
        payload.global_discount_percent or 0.0,
    )

    record = {
        "id":                       q_id,
        "status":                   QuotationStatus.DRAFT,
        "branding":                 payload.branding,
        "client_name":              payload.client_name,
        "client_email":             payload.client_email,
        "client_address":           payload.client_address,
        "line_items":               payload.line_items,
        "tax_percent":              payload.tax_percent or 0.0,
        "global_discount_percent":  payload.global_discount_percent or 0.0,
        "subtotal":                 subtotal,
        "discount_amount":          discount_amount,
        "tax_amount":               tax_amount,
        "total":                    total,
        "valid_until":              payload.valid_until,
        "notes":                    payload.notes,
        "payment_terms":            payload.payment_terms or "Net 30",
        "created_at":               datetime.utcnow().isoformat(),
    }
    _quotations[q_id] = record
    return QuotationResponse(**record)


# ─────────────────────────────────────────────────────────────────────────────
# GET /list
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/list", response_model=List[QuotationResponse], summary="List all quotations")
def list_quotations(
    status: Optional[QuotationStatus] = Query(None, description="Filter by status"),
):
    """Return all quotations, optionally filtered by status."""
    results = list(_quotations.values())
    if status:
        results = [q for q in results if q["status"] == status]
    return [QuotationResponse(**q) for q in results]


# ─────────────────────────────────────────────────────────────────────────────
# GET /{id}
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{quotation_id}", response_model=QuotationResponse, summary="Get a quotation by ID")
def get_quotation(quotation_id: str):
    """Retrieve a single quotation by its ID."""
    if quotation_id not in _quotations:
        raise HTTPException(status_code=404, detail=f"Quotation '{quotation_id}' not found.")
    return QuotationResponse(**_quotations[quotation_id])


# ─────────────────────────────────────────────────────────────────────────────
# PUT /{id}/approve
# ─────────────────────────────────────────────────────────────────────────────
@router.put("/{quotation_id}/approve", response_model=ApproveRejectResponse, summary="Approve a quotation")
def approve_quotation(quotation_id: str):
    """Mark a quotation as approved (approval workflow)."""
    if quotation_id not in _quotations:
        raise HTTPException(status_code=404, detail=f"Quotation '{quotation_id}' not found.")
    q = _quotations[quotation_id]
    if q["status"] == QuotationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Quotation is already approved.")
    q["status"] = QuotationStatus.APPROVED
    return ApproveRejectResponse(id=quotation_id, status=QuotationStatus.APPROVED,
                                  message="Quotation approved successfully.")


# ─────────────────────────────────────────────────────────────────────────────
# PUT /{id}/reject
# ─────────────────────────────────────────────────────────────────────────────
@router.put("/{quotation_id}/reject", response_model=ApproveRejectResponse, summary="Reject a quotation")
def reject_quotation(quotation_id: str):
    """Mark a quotation as rejected."""
    if quotation_id not in _quotations:
        raise HTTPException(status_code=404, detail=f"Quotation '{quotation_id}' not found.")
    q = _quotations[quotation_id]
    if q["status"] == QuotationStatus.REJECTED:
        raise HTTPException(status_code=400, detail="Quotation is already rejected.")
    q["status"] = QuotationStatus.REJECTED
    return ApproveRejectResponse(id=quotation_id, status=QuotationStatus.REJECTED,
                                  message="Quotation rejected.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /{id}/send-email
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/{quotation_id}/send-email", response_model=SendEmailResponse,
             summary="Email the quotation PDF to the client")
def send_quotation_email(quotation_id: str, payload: SendEmailRequest):
    """
    Generate the quotation PDF and email it to the client (or a custom address).
    Falls back to dry-run mode if SMTP credentials are not set in .env.
    """
    if quotation_id not in _quotations:
        raise HTTPException(status_code=404, detail=f"Quotation '{quotation_id}' not found.")

    q = _quotations[quotation_id]
    recipient = payload.recipient_email or q["client_email"]
    subject   = payload.subject or f"Quotation {quotation_id} from {q['branding'].company_name}"
    body      = payload.body or (
        f"Dear {q['client_name']},\n\n"
        f"Please find attached your quotation {quotation_id}.\n\n"
        f"Total: PKR {q['total']:,.2f}\n"
        f"Valid Until: {q['valid_until'] or 'N/A'}\n\n"
        "Kind regards,\n" + q['branding'].company_name
    )

    pdf_bytes = generate_quotation_pdf(
        {**q, "branding": q["branding"].model_dump(), "line_items": [li.model_dump() for li in q["line_items"]]}
    )
    result = send_document_email(
        recipient_email=recipient,
        subject=subject,
        body=body,
        pdf_bytes=pdf_bytes,
        attachment_filename=f"Quotation-{quotation_id}.pdf",
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    q["status"] = QuotationStatus.SENT
    return SendEmailResponse(id=quotation_id, message=result["message"], recipient_email=recipient)


# ─────────────────────────────────────────────────────────────────────────────
# GET /{id}/pdf
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{quotation_id}/pdf", summary="Download quotation as PDF",
            response_class=Response)
def download_quotation_pdf(quotation_id: str):
    """
    Generate and return the quotation as a downloadable PDF file.
    """
    if quotation_id not in _quotations:
        raise HTTPException(status_code=404, detail=f"Quotation '{quotation_id}' not found.")

    q = _quotations[quotation_id]
    pdf_bytes = generate_quotation_pdf(
        {**q, "branding": q["branding"].model_dump(), "line_items": [li.model_dump() for li in q["line_items"]]}
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Quotation-{quotation_id}.pdf"'},
    )
