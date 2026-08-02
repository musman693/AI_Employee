"""
email_service.py — Email delivery for Quotations and Invoices.

Currently implemented with smtplib (standard library) + SMTP credentials from .env.
The `send_document_email` function attaches a PDF and sends it to the recipient.

If SMTP credentials are not configured, the service returns a "dry-run" success so the
module works end-to-end during development without requiring live email credentials.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Config from .env ──────────────────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def send_document_email(
    recipient_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    attachment_filename: str = "document.pdf",
) -> dict:
    """
    Send an email with a PDF attachment.

    Args:
        recipient_email:     Destination email address.
        subject:             Email subject line.
        body:                Plain-text email body.
        pdf_bytes:           Raw bytes of the PDF to attach.
        attachment_filename: Filename for the attachment (e.g. "Invoice-INV-001.pdf").

    Returns:
        dict with keys: success (bool), message (str)
    """

    # Dry-run mode — no SMTP credentials configured
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning(
            "SMTP credentials not set. Email NOT sent (dry-run). "
            "Set SMTP_USER and SMTP_PASSWORD in .env to enable real delivery."
        )
        return {
            "success": True,
            "message": (
                f"[DRY-RUN] Email to {recipient_email} prepared successfully. "
                "Configure SMTP_USER and SMTP_PASSWORD in .env to send real emails."
            ),
        }

    try:
        msg = MIMEMultipart()
        msg["From"]    = SMTP_USER
        msg["To"]      = recipient_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_part.add_header(
            "Content-Disposition",
            "attachment",
            filename=attachment_filename,
        )
        msg.attach(pdf_part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient_email, msg.as_string())

        logger.info(f"Email sent successfully to {recipient_email}")
        return {"success": True, "message": f"Email delivered to {recipient_email}"}

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check SMTP_USER/SMTP_PASSWORD in .env")
        return {"success": False, "message": "SMTP authentication failed. Check credentials in .env."}

    except Exception as exc:
        logger.exception(f"Failed to send email to {recipient_email}: {exc}")
        return {"success": False, "message": f"Email delivery failed: {str(exc)}"}
