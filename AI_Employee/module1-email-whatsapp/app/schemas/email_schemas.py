from pydantic import BaseModel, Field


class EmailDraftRequest(BaseModel):
    instruction: str = Field(..., min_length=3, max_length=500)


class EmailDraftResponse(BaseModel):
    subject: str
    body: str


class EmailAutoReplyRequest(BaseModel):
    thread_id: str | None = None
    sender: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class EmailAutoReplyResponse(BaseModel):
    reply: str


class EmailSummarizeRequest(BaseModel):
    messages: list[str] = Field(..., min_items=1)


class EmailSummarizeResponse(BaseModel):
    summary: str


class EmailClassifyRequest(BaseModel):
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class EmailClassifyResponse(BaseModel):
    category: str
    confidence: float


class EmailPrioritizeRequest(BaseModel):
    emails: list[str] = Field(..., min_items=1)


class PriorityItem(BaseModel):
    email: str
    score: int


class EmailPrioritizeResponse(BaseModel):
    ranked_emails: list[PriorityItem]


class EmailFollowUpRequest(BaseModel):
    instruction: str = Field(..., min_length=3)


class EmailFollowUpResponse(BaseModel):
    suggestion: str
