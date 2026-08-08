from pydantic import BaseModel, Field


class WhatsAppSupportReplyRequest(BaseModel):
    message: str = Field(..., min_length=1)
    customer_name: str | None = None


class WhatsAppSupportReplyResponse(BaseModel):
    reply: str


class WhatsAppOrderConfirmationRequest(BaseModel):
    order_id: str = Field(..., min_length=1)
    customer_name: str | None = None


class WhatsAppOrderConfirmationResponse(BaseModel):
    reply: str


class WhatsAppRecommendRequest(BaseModel):
    customer_context: str = Field(..., min_length=1)


class WhatsAppRecommendResponse(BaseModel):
    recommendation: str


class WhatsAppSendInvoiceRequest(BaseModel):
    customer_name: str = Field(..., min_length=1)
    invoice_id: str = Field(..., min_length=1)


class WhatsAppSendInvoiceResponse(BaseModel):
    status: str
    message: str


class WhatsAppVoiceMessageRequest(BaseModel):
    transcription: str = Field(..., min_length=1)


class WhatsAppVoiceMessageResponse(BaseModel):
    intent: str
    response: str


class WhatsAppWebhookRequest(BaseModel):
    entry: list[dict] = Field(default_factory=list)
