"""
qr_service.py — QR code generation for invoice payment links.
Uses the `qrcode` library with PIL backend.
Returns raw PNG image bytes that can be embedded in PDF or returned as an API response.
"""

import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
import base64


def generate_qr_bytes(data: str, box_size: int = 6, border: int = 2) -> bytes:
    """
    Generate a QR code for the given data string.

    Args:
        data:      The URL or text to encode (e.g. a payment link).
        box_size:  Pixel size of each QR module (default 6).
        border:    Quiet-zone thickness in modules (default 2).

    Returns:
        Raw PNG bytes of the QR code image.
    """
    qr = qrcode.QRCode(
        version=None,           # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_qr_base64(data: str) -> str:
    """
    Generate a QR code and return it as a base64-encoded PNG string.
    Useful for embedding in JSON API responses or HTML <img src="data:image/png;base64,...">

    Args:
        data: The URL or text to encode.

    Returns:
        Base64-encoded PNG string (no data URI prefix).
    """
    png_bytes = generate_qr_bytes(data)
    return base64.b64encode(png_bytes).decode("utf-8")
