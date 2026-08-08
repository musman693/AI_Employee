from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.whatsapp_schemas import (
    WhatsAppOrderConfirmationRequest,
    WhatsAppOrderConfirmationResponse,
    WhatsAppRecommendRequest,
    WhatsAppRecommendResponse,
    WhatsAppSendInvoiceRequest,
    WhatsAppSendInvoiceResponse,
    WhatsAppSupportReplyRequest,
    WhatsAppSupportReplyResponse,
    WhatsAppVoiceMessageRequest,
    WhatsAppVoiceMessageResponse,
    WhatsAppWebhookRequest,
)
from app.services.whatsapp_service import WhatsAppService
from app.services.whisper_service import WhisperService

router = APIRouter()
whatsapp_service = WhatsAppService()
whisper_service = WhisperService()


@router.post("/whatsapp/support-reply", response_model=WhatsAppSupportReplyResponse, dependencies=[Depends(get_current_user)])
async def support_reply(request: WhatsAppSupportReplyRequest) -> WhatsAppSupportReplyResponse:
    reply = f"Hello {request.customer_name or 'there'}, we are reviewing your request."
    return WhatsAppSupportReplyResponse(reply=reply)


@router.post("/whatsapp/order-confirmation", response_model=WhatsAppOrderConfirmationResponse, dependencies=[Depends(get_current_user)])
async def order_confirmation(request: WhatsAppOrderConfirmationRequest) -> WhatsAppOrderConfirmationResponse:
    reply = f"Your order {request.order_id} has been confirmed."
    return WhatsAppOrderConfirmationResponse(reply=reply)


@router.post("/whatsapp/recommend", response_model=WhatsAppRecommendResponse, dependencies=[Depends(get_current_user)])
async def recommend(request: WhatsAppRecommendRequest) -> WhatsAppRecommendResponse:
    return WhatsAppRecommendResponse(recommendation=f"Based on your context, we recommend a tailored offer for: {request.customer_context}")


@router.post("/whatsapp/send-invoice", response_model=WhatsAppSendInvoiceResponse, dependencies=[Depends(get_current_user)])
async def send_invoice(request: WhatsAppSendInvoiceRequest) -> WhatsAppSendInvoiceResponse:
    return WhatsAppSendInvoiceResponse(status="queued", message=f"Invoice {request.invoice_id} will be sent to {request.customer_name}")


@router.post("/whatsapp/voice-message", response_model=WhatsAppVoiceMessageResponse, dependencies=[Depends(get_current_user)])
async def voice_message(request: WhatsAppVoiceMessageRequest) -> WhatsAppVoiceMessageResponse:
    transcription = request.transcription
    return WhatsAppVoiceMessageResponse(intent="support_request", response=f"We understood: {transcription}")


@router.post("/whatsapp/webhook", status_code=200, dependencies=[Depends(get_current_user)])
async def whatsapp_webhook(payload: WhatsAppWebhookRequest) -> dict[str, str]:
    await whatsapp_service.receive_webhook(payload.model_dump())
    return {"status": "received"}
