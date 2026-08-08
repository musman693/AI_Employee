"""
invoice.py — AI Invoice Generator API endpoints.

Endpoints:
  POST   /api/v1/invoice/create                 Create a new invoice
  GET    /api/v1/invoice/list                   List all invoices (with filters)
  GET    /api/v1/invoice/overdue                Get all overdue invoices
  POST   /api/v1/invoice/recurring              Create a recurring invoice schedule
  GET    /api/v1/invoice/{id}                   Get invoice by ID
  PUT    /api/v1/invoice/{id}/mark-paid         Mark invoice as paid
  POST   /api/v1/invoice/{id}/payment-reminder  Send a due-date reminder
  GET    /api/v1/invoice/{id}/pdf               Download invoice as PDF (with QR code)
"""

import uuid
from datetime import datetime, date
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.models.invoice_models import (
    CreateInvoiceRequest, InvoiceResponse, InvoiceStatus,
    MarkPaidResponse, ReminderResponse,
    RecurringInvoiceRequest, RecurringInvoiceResponse,
)
from app.services.pdf_service import generate_invoice_pdf
from app.services.qr_service import generate_qr_bytes, generate_qr_base64
from app.services.email_service import send_document_email

router = APIRouter()

# ── In-memory stores ──────────────────────────────────────────────────────────
_invoices:   dict[str, dict] = {}
_recurring:  dict[str, dict] = {}

_invoice_counter = 0


def _next_invoice_number() -> str:
    global _invoice_counter
    _invoice_counter += 1
    return f"INV-{_invoice_counter:05d}"


def _compute_totals(line_items, tax_percent):
    subtotal = 0.0
    for item in line_items:
        qty   = item.quantity
        price = item.unit_price
        disc  = item.discount_percent or 0.0
        subtotal += qty * price * (1 - disc / 100)
    tax_amount = subtotal * (tax_percent / 100)
    total = subtotal + tax_amount
    return subtotal, tax_amount, total


def _is_overdue(inv: dict) -> bool:
    if inv["status"] in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
        return False
    if inv.get("due_date") is None:
        return False
    due = inv["due_date"]
    if isinstance(due, str):
        due = date.fromisoformat(due)
    return due < date.today()


# ─────────────────────────────────────────────────────────────────────────────
# POST /create
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/create", response_model=InvoiceResponse, summary="Create a new invoice")
def create_invoice(payload: CreateInvoiceRequest):
    """
    Create a new invoice with line items, tax, due date, payment link,
    and an auto-generated QR code (if payment_link is provided).
    """
    inv_id  = f"INV-{uuid.uuid4().hex[:8].upper()}"
    inv_num = _next_invoice_number()
    subtotal, tax_amount, total = _compute_totals(payload.line_items, payload.tax_percent or 0.0)

    # Generate QR code if payment link is present
    qr_base64 = None
    if payload.payment_link:
        qr_base64 = generate_qr_base64(payload.payment_link)

    record = {
        "id":               inv_id,
        "invoice_number":   inv_num,
        "status":           InvoiceStatus.DRAFT,
        "company_name":     payload.company_name,
        "company_address":  payload.company_address,
        "company_email":    payload.company_email,
        "company_phone":    payload.company_phone,
        "client_name":      payload.client_name,
        "client_email":     payload.client_email,
        "client_address":   payload.client_address,
        "line_items":       payload.line_items,
        "tax_percent":      payload.tax_percent or 0.0,
        "subtotal":         subtotal,
        "tax_amount":       tax_amount,
        "total":            total,
        "due_date":         payload.due_date,
        "payment_link":     payload.payment_link,
        "notes":            payload.notes,
        "qr_code_base64":   qr_base64,
        "created_at":       datetime.utcnow().isoformat(),
        "paid_at":          None,
    }
    _invoices[inv_id] = record
    return InvoiceResponse(**record)


# ─────────────────────────────────────────────────────────────────────────────
# GET /list
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/list", response_model=List[InvoiceResponse], summary="List all invoices")
def list_invoices(
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
):
    """Return all invoices, optionally filtered by status. Overdue invoices are auto-flagged."""
    for inv in _invoices.values():
        if _is_overdue(inv):
            inv["status"] = InvoiceStatus.OVERDUE
    results = list(_invoices.values())
    if status:
        results = [i for i in results if i["status"] == status]
    return [InvoiceResponse(**i) for i in results]


# ─────────────────────────────────────────────────────────────────────────────
# GET /overdue
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/overdue", response_model=List[InvoiceResponse], summary="Get all overdue invoices")
def get_overdue_invoices():
    """Return all invoices whose due date has passed and are not yet paid."""
    overdue = []
    for inv in _invoices.values():
        if _is_overdue(inv):
            inv["status"] = InvoiceStatus.OVERDUE
            overdue.append(InvoiceResponse(**inv))
    return overdue


# ─────────────────────────────────────────────────────────────────────────────
# POST /recurring
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/recurring", response_model=RecurringInvoiceResponse,
             summary="Create a recurring invoice schedule")
def create_recurring_invoice(payload: RecurringInvoiceRequest):
    """
    Schedule an existing invoice to recur at a defined frequency (weekly/monthly/quarterly/yearly).
    The `auto_send` flag controls whether future invoices are emailed automatically.
    """
    if payload.base_invoice_id not in _invoices:
        raise HTTPException(
            status_code=404,
            detail=f"Base invoice '{payload.base_invoice_id}' not found."
        )
    rec_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
    record = {
        "recurring_id":    rec_id,
        "base_invoice_id": payload.base_invoice_id,
        "frequency":       payload.frequency,
        "start_date":      payload.start_date,
        "end_date":        payload.end_date,
        "auto_send":       payload.auto_send,
        "message": (
            f"Recurring invoice scheduled every {payload.frequency.value} "
            f"starting {payload.start_date}."
        ),
    }
    _recurring[rec_id] = record
    return RecurringInvoiceResponse(**record)


# ─────────────────────────────────────────────────────────────────────────────
# GET /{id}
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{invoice_id}", response_model=InvoiceResponse, summary="Get an invoice by ID")
def get_invoice(invoice_id: str):
    """Retrieve a single invoice by its ID."""
    if invoice_id not in _invoices:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found.")
    inv = _invoices[invoice_id]
    if _is_overdue(inv):
        inv["status"] = InvoiceStatus.OVERDUE
    return InvoiceResponse(**inv)


# ─────────────────────────────────────────────────────────────────────────────
# PUT /{id}/mark-paid
# ─────────────────────────────────────────────────────────────────────────────
@router.put("/{invoice_id}/mark-paid", response_model=MarkPaidResponse,
            summary="Mark an invoice as paid")
def mark_invoice_paid(invoice_id: str):
    """Mark an invoice as paid and record the payment timestamp."""
    if invoice_id not in _invoices:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found.")
    inv = _invoices[invoice_id]
    if inv["status"] == InvoiceStatus.PAID:
        raise HTTPException(status_code=400, detail="Invoice is already marked as paid.")
    paid_at = datetime.utcnow().isoformat()
    inv["status"]  = InvoiceStatus.PAID
    inv["paid_at"] = paid_at
    return MarkPaidResponse(
        id=invoice_id,
        status=InvoiceStatus.PAID,
        paid_at=paid_at,
        message="Invoice marked as paid successfully.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /{id}/payment-reminder
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/{invoice_id}/payment-reminder", response_model=ReminderResponse,
             summary="Send a payment due-date reminder")
def send_payment_reminder(invoice_id: str):
    """
    Send a payment reminder email to the client for the given invoice.
    Works in dry-run mode if SMTP credentials are not configured.
    """
    if invoice_id not in _invoices:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found.")
    inv = _invoices[invoice_id]
    if inv["status"] == InvoiceStatus.PAID:
        raise HTTPException(status_code=400, detail="Invoice is already paid — no reminder needed.")

    subject = f"Payment Reminder: Invoice {inv['invoice_number']} Due"
    due_str = str(inv.get("due_date", "N/A"))
    body = (
        f"Dear {inv['client_name']},\n\n"
        f"This is a reminder that invoice {inv['invoice_number']} "
        f"for PKR {inv['total']:,.2f} is due on {due_str}.\n\n"
        f"Payment Link: {inv.get('payment_link', 'Please contact us for payment details.')}\n\n"
        f"Kind regards,\n{inv['company_name']}"
    )

    # Generate invoice PDF to attach
    pdf_bytes = generate_invoice_pdf(
        {**inv, "line_items": [li.model_dump() for li in inv["line_items"]]}
    )

    result = send_document_email(
        recipient_email=inv["client_email"],
        subject=subject,
        body=body,
        pdf_bytes=pdf_bytes,
        attachment_filename=f"Invoice-{inv['invoice_number']}.pdf",
    )

    return ReminderResponse(
        id=invoice_id,
        message=result["message"],
        client_email=inv["client_email"],
        due_date=due_str,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /{id}/pdf
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{invoice_id}/pdf", summary="Download invoice as PDF",
            response_class=Response)
def download_invoice_pdf(invoice_id: str):
    """
    Generate and return the invoice as a downloadable PDF.
    If the invoice has a payment_link, a QR code is embedded in the PDF.
    """
    if invoice_id not in _invoices:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found.")

    inv = _invoices[invoice_id]

    qr_bytes = None
    if inv.get("payment_link"):
        qr_bytes = generate_qr_bytes(inv["payment_link"])

    pdf_bytes = generate_invoice_pdf(
        {**inv, "line_items": [li.model_dump() for li in inv["line_items"]]},
        qr_image_bytes=qr_bytes,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Invoice-{inv["invoice_number"]}.pdf"'},
    )
