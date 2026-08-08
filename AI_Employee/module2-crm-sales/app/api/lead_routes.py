from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_with_permission
from app.db.session import get_db
from app.models.customer import Customer
from app.models.lead import Lead
from app.schemas.customer_schemas import CustomerRead
from app.schemas.lead_schemas import LeadConvertResponse, LeadCreate, LeadRead, LeadUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("leads:write")),
) -> LeadRead:
    lead = Lead(**payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadRead.model_validate(lead)


@router.get("", response_model=list[LeadRead])
async def list_leads(
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("leads:read")),
    status_filter: str | None = Query(default=None, alias="status"),
    owner: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[LeadRead]:
    query = db.query(Lead).filter(Lead.deleted_at.is_(None))
    if status_filter:
        query = query.filter(Lead.status == status_filter)
    if owner:
        query = query.filter(Lead.assigned_to == owner)
    if created_after:
        query = query.filter(Lead.created_at >= created_after)
    if created_before:
        query = query.filter(Lead.created_at <= created_before)
    leads = query.offset(skip).limit(limit).all()
    return [LeadRead.model_validate(lead) for lead in leads]


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("leads:write")),
) -> LeadRead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return LeadRead.model_validate(lead)


@router.post("/{lead_id}/convert", response_model=LeadConvertResponse)
async def convert_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("leads:write")),
) -> LeadConvertResponse:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    customer_payload = {
        "name": lead.name,
        "company": lead.company,
        "email": lead.email,
        "owner_id": lead.assigned_to,
        "tags": [lead.source or "lead"],
    }
    service = CustomerService(db)
    customer = service.create(customer_payload)
    lead.converted_customer_id = customer.id
    lead.status = "converted"
    db.commit()
    db.refresh(lead)
    return LeadConvertResponse(
        lead=LeadRead.model_validate(lead),
        customer=CustomerRead.model_validate(customer).model_dump(),
    )
