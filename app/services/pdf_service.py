"""
pdf_service.py — PDF generation for Quotations and Invoices using ReportLab.
Supports company branding, line items table, tax/discount breakdown, and QR code embed.
"""

from io import BytesIO
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, Image as RLImage
)
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER


# ─── Colour palette ───────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor("#1A3C5E")   # dark navy — header / accents
ACCENT    = colors.HexColor("#2E86AB")   # teal — table header row
LIGHT_BG  = colors.HexColor("#F4F7FA")   # very light blue-grey — alt rows
WHITE     = colors.white
BLACK     = colors.HexColor("#1C1C1C")
GREY      = colors.HexColor("#7A7A7A")


def _styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=PRIMARY,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontSize=9,
        textColor=GREY,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=8,
        textColor=GREY,
        spaceAfter=1,
    )
    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BLACK,
    )
    right_style = ParagraphStyle(
        "Right",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BLACK,
        alignment=TA_RIGHT,
    )
    total_style = ParagraphStyle(
        "Total",
        parent=styles["Normal"],
        fontSize=13,
        textColor=PRIMARY,
        alignment=TA_RIGHT,
        fontName="Helvetica-Bold",
    )
    note_style = ParagraphStyle(
        "Note",
        parent=styles["Normal"],
        fontSize=9,
        textColor=GREY,
    )
    return {
        "title": title_style, "sub": sub_style,
        "label": label_style, "value": value_style,
        "right": right_style, "total": total_style,
        "note": note_style,
    }


def _calc_totals(line_items: list, tax_percent: float, global_discount_percent: float = 0.0):
    subtotal = 0.0
    for item in line_items:
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0)
        disc = item.get("discount_percent", 0)
        subtotal += qty * price * (1 - disc / 100)

    discount_amount = subtotal * (global_discount_percent / 100)
    after_discount = subtotal - discount_amount
    tax_amount = after_discount * (tax_percent / 100)
    total = after_discount + tax_amount
    return subtotal, discount_amount, tax_amount, total


def generate_quotation_pdf(quotation: dict, qr_image_bytes: Optional[bytes] = None) -> bytes:
    """Generate a professional quotation PDF. Returns raw PDF bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    s = _styles()
    story = []

    branding = quotation.get("branding", {})

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(branding.get("company_name", "Your Company"), s["title"]))
    story.append(Paragraph(branding.get("address", ""), s["sub"]))
    story.append(Paragraph(branding.get("phone", "") + "  |  " + branding.get("email", ""), s["sub"]))
    if branding.get("website"):
        story.append(Paragraph(branding["website"], s["sub"]))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=10))

    # ── Quotation meta ────────────────────────────────────────────────────────
    meta_data = [
        [Paragraph("<b>QUOTATION</b>", ParagraphStyle("H", fontSize=18, textColor=PRIMARY, fontName="Helvetica-Bold")),
         Paragraph(f"<b>#{quotation.get('id', 'QUO-001')}</b>", ParagraphStyle("HR", fontSize=12, textColor=GREY, alignment=TA_RIGHT))],
        [Paragraph(f"Date: {datetime.now().strftime('%d %b %Y')}", s["sub"]),
         Paragraph(f"Valid Until: {quotation.get('valid_until', 'N/A')}", ParagraphStyle("SR", fontSize=9, textColor=GREY, alignment=TA_RIGHT))],
    ]
    meta_table = Table(meta_data, colWidths=["60%", "40%"])
    meta_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # ── Bill To ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Bill To:", s["label"]))
    story.append(Paragraph(f"<b>{quotation.get('client_name', '')}</b>", s["value"]))
    story.append(Paragraph(quotation.get("client_email", ""), s["sub"]))
    if quotation.get("client_address"):
        story.append(Paragraph(quotation["client_address"], s["sub"]))
    story.append(Spacer(1, 14))

    # ── Line Items Table ──────────────────────────────────────────────────────
    headers = ["#", "Description", "Qty", "Unit Price", "Disc %", "Amount"]
    table_data = [headers]
    line_items = quotation.get("line_items", [])
    for i, item in enumerate(line_items, 1):
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0)
        disc = item.get("discount_percent", 0)
        amount = qty * price * (1 - disc / 100)
        table_data.append([
            str(i),
            item.get("description", ""),
            f"{qty:.2f}",
            f"PKR {price:,.2f}",
            f"{disc:.1f}%",
            f"PKR {amount:,.2f}",
        ])

    col_widths = [1*cm, 6.5*cm, 1.5*cm, 2.8*cm, 1.5*cm, 3*cm]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("ALIGN",        (2, 0), (-1, -1), "RIGHT"),
        ("ALIGN",        (0, 0), (1, -1), "LEFT"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID",         (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    # ── Totals ────────────────────────────────────────────────────────────────
    tax_pct  = quotation.get("tax_percent", 0)
    disc_pct = quotation.get("global_discount_percent", 0)
    subtotal, disc_amt, tax_amt, total = _calc_totals(line_items, tax_pct, disc_pct)

    totals_data = [
        ["Subtotal", f"PKR {subtotal:,.2f}"],
    ]
    if disc_pct:
        totals_data.append([f"Global Discount ({disc_pct}%)", f"- PKR {disc_amt:,.2f}"])
    if tax_pct:
        totals_data.append([f"Tax ({tax_pct}%)", f"PKR {tax_amt:,.2f}"])
    totals_data.append(["TOTAL DUE", f"PKR {total:,.2f}"])

    totals_table = Table(totals_data, colWidths=[13*cm, 3.6*cm])
    totals_style = [
        ("ALIGN",      (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE",   (0, 0), (-1, -2), 9),
        ("FONTSIZE",   (0, -1), (-1, -1), 12),
        ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (0, -1), (-1, -1), PRIMARY),
        ("LINEABOVE",  (0, -1), (-1, -1), 1.5, PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]
    totals_table.setStyle(TableStyle(totals_style))
    story.append(totals_table)
    story.append(Spacer(1, 20))

    # ── Notes / Payment Terms ─────────────────────────────────────────────────
    if quotation.get("payment_terms"):
        story.append(Paragraph(f"<b>Payment Terms:</b> {quotation['payment_terms']}", s["note"]))
    if quotation.get("notes"):
        story.append(Paragraph(f"<b>Notes:</b> {quotation['notes']}", s["note"]))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
    story.append(Paragraph("Thank you for your business!", ParagraphStyle(
        "Footer", fontSize=9, textColor=GREY, alignment=TA_CENTER)))

    doc.build(story)
    return buffer.getvalue()


def generate_invoice_pdf(invoice: dict, qr_image_bytes: Optional[bytes] = None) -> bytes:
    """Generate a professional invoice PDF with optional QR code. Returns raw PDF bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    s = _styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(invoice.get("company_name", "Your Company"), s["title"]))
    story.append(Paragraph(invoice.get("company_address", ""), s["sub"]))
    story.append(Paragraph(invoice.get("company_phone", "") + "  |  " + invoice.get("company_email", ""), s["sub"]))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=10))

    # ── Invoice meta ──────────────────────────────────────────────────────────
    meta_data = [
        [Paragraph("<b>INVOICE</b>", ParagraphStyle("H", fontSize=18, textColor=PRIMARY, fontName="Helvetica-Bold")),
         Paragraph(f"<b>{invoice.get('invoice_number', 'INV-001')}</b>", ParagraphStyle("HR", fontSize=12, textColor=GREY, alignment=TA_RIGHT))],
        [Paragraph(f"Date: {datetime.now().strftime('%d %b %Y')}", s["sub"]),
         Paragraph(f"Due: {invoice.get('due_date', 'N/A')}", ParagraphStyle("SR", fontSize=9, textColor=GREY, alignment=TA_RIGHT))],
        [Paragraph(f"Status: <b>{invoice.get('status', 'sent').upper()}</b>", s["sub"]), Paragraph("", s["sub"])],
    ]
    meta_table = Table(meta_data, colWidths=["60%", "40%"])
    meta_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # ── Bill To ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Bill To:", s["label"]))
    story.append(Paragraph(f"<b>{invoice.get('client_name', '')}</b>", s["value"]))
    story.append(Paragraph(invoice.get("client_email", ""), s["sub"]))
    if invoice.get("client_address"):
        story.append(Paragraph(invoice["client_address"], s["sub"]))
    story.append(Spacer(1, 14))

    # ── Line Items Table ──────────────────────────────────────────────────────
    headers = ["#", "Description", "Qty", "Unit Price", "Disc %", "Amount"]
    table_data = [headers]
    line_items = invoice.get("line_items", [])
    for i, item in enumerate(line_items, 1):
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0)
        disc = item.get("discount_percent", 0)
        amount = qty * price * (1 - disc / 100)
        table_data.append([
            str(i),
            item.get("description", ""),
            f"{qty:.2f}",
            f"PKR {price:,.2f}",
            f"{disc:.1f}%",
            f"PKR {amount:,.2f}",
        ])

    col_widths = [1*cm, 6.5*cm, 1.5*cm, 2.8*cm, 1.5*cm, 3*cm]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("ALIGN",        (2, 0), (-1, -1), "RIGHT"),
        ("ALIGN",        (0, 0), (1, -1), "LEFT"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("GRID",         (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    # ── Totals ────────────────────────────────────────────────────────────────
    tax_pct = invoice.get("tax_percent", 0)
    subtotal, _, tax_amt, total = _calc_totals(line_items, tax_pct)

    totals_data = [["Subtotal", f"PKR {subtotal:,.2f}"]]
    if tax_pct:
        totals_data.append([f"Tax ({tax_pct}%)", f"PKR {tax_amt:,.2f}"])
    totals_data.append(["TOTAL DUE", f"PKR {total:,.2f}"])
    if invoice.get("status") == "paid":
        totals_data.append(["PAID ✓", f"PKR {total:,.2f}"])

    totals_table = Table(totals_data, colWidths=[13*cm, 3.6*cm])
    totals_table.setStyle(TableStyle([
        ("ALIGN",      (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE",   (0, 0), (-1, -2), 9),
        ("FONTSIZE",   (0, -1), (-1, -1), 12),
        ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (0, -1), (-1, -1), PRIMARY),
        ("LINEABOVE",  (0, -1), (-1, -1), 1.5, PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 16))

    # ── QR Code + Payment Link ────────────────────────────────────────────────
    if qr_image_bytes or invoice.get("payment_link"):
        qr_section = []
        if qr_image_bytes:
            qr_buf = BytesIO(qr_image_bytes)
            qr_img = RLImage(qr_buf, width=2.5*cm, height=2.5*cm)
            qr_section.append(qr_img)
        if invoice.get("payment_link"):
            qr_section.append(Paragraph(
                f'<b>Pay Online:</b> <a href="{invoice["payment_link"]}">{invoice["payment_link"]}</a>',
                s["note"]
            ))
        for el in qr_section:
            story.append(el)
        story.append(Spacer(1, 10))

    # ── Notes ─────────────────────────────────────────────────────────────────
    if invoice.get("notes"):
        story.append(Paragraph(f"<b>Notes:</b> {invoice['notes']}", s["note"]))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
    story.append(Paragraph("Thank you for your business!", ParagraphStyle(
        "Footer", fontSize=9, textColor=GREY, alignment=TA_CENTER)))

    doc.build(story)
    return buffer.getvalue()
