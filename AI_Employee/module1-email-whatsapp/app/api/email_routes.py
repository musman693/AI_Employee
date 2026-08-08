from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.email_schemas import (
    EmailAutoReplyRequest,
    EmailAutoReplyResponse,
    EmailClassifyRequest,
    EmailClassifyResponse,
    EmailDraftRequest,
    EmailDraftResponse,
    EmailFollowUpRequest,
    EmailFollowUpResponse,
    EmailPrioritizeRequest,
    EmailPrioritizeResponse,
    EmailSummarizeRequest,
    EmailSummarizeResponse,
)
from app.services.ai_provider import (
    AIProviderError,
    classify,
    follow_up_suggestion,
    generate_reply,
    prioritize,
    summarize,
)

router = APIRouter()


@router.post("/email/draft", response_model=EmailDraftResponse, dependencies=[Depends(get_current_user)])
async def draft_email(request: EmailDraftRequest) -> EmailDraftResponse:
    subject = f"Draft for: {request.instruction[:40]}"
    body = f"Hi,\n\n{request.instruction}\n\nBest regards,"
    return EmailDraftResponse(subject=subject, body=body)


@router.post("/email/auto-reply", response_model=EmailAutoReplyResponse, dependencies=[Depends(get_current_user)])
async def auto_reply(request: EmailAutoReplyRequest) -> EmailAutoReplyResponse:
    try:
        reply_text = await generate_reply(request.body, context=request.subject)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmailAutoReplyResponse(reply=reply_text)


@router.post("/email/summarize", response_model=EmailSummarizeResponse, dependencies=[Depends(get_current_user)])
async def summarize_email(request: EmailSummarizeRequest) -> EmailSummarizeResponse:
    try:
        summary = await summarize(request.messages)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmailSummarizeResponse(summary=summary)


@router.post("/email/classify", response_model=EmailClassifyResponse, dependencies=[Depends(get_current_user)])
async def classify_email(request: EmailClassifyRequest) -> EmailClassifyResponse:
    try:
        category, confidence = await classify(request.subject, request.body)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmailClassifyResponse(category=category, confidence=confidence)


@router.post("/email/prioritize", response_model=EmailPrioritizeResponse, dependencies=[Depends(get_current_user)])
async def prioritize_emails(request: EmailPrioritizeRequest) -> EmailPrioritizeResponse:
    try:
        ranked = await prioritize(request.emails)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmailPrioritizeResponse(ranked_emails=[{"email": item["email"], "score": item["score"]} for item in ranked])


@router.post("/email/follow-up", response_model=EmailFollowUpResponse, dependencies=[Depends(get_current_user)])
async def follow_up(request: EmailFollowUpRequest) -> EmailFollowUpResponse:
    try:
        suggestion = await follow_up_suggestion(request.instruction)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return EmailFollowUpResponse(suggestion=suggestion)
