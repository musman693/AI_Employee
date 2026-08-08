from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_with_permission
from app.db.session import get_db
from app.models.activity import Activity
from app.models.customer import Customer
from app.models.deal import Deal
from app.schemas.customer_schemas import CustomerCreate, CustomerListResponse, CustomerRead, CustomerUpdate
from app.services.customer_service import CustomerService
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("customers:write")),
) -> CustomerRead:
    service = CustomerService(db)
    customer = service.create(payload.model_dump())
    return CustomerRead.model_validate(customer)


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("customers:read")),
    search: str | None = Query(default=None),
    tag: str | None = None,
    owner: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    skip: int = 0,
    limit: int = 20,
) -> CustomerListResponse:
    query = db.query(Customer).filter(Customer.deleted_at.is_(None))
    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%"))
    if tag:
        query = query.filter(Customer.tags.contains([tag]))
    if owner:
        query = query.filter(Customer.owner_id == owner)
    if created_after:
        query = query.filter(Customer.created_at >= created_after)
    if created_before:
        query = query.filter(Customer.created_at <= created_before)
    items = query.offset(skip).limit(limit).all()
    total = query.count()
    return CustomerListResponse(items=[CustomerRead.model_validate(item) for item in items], total=total)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("customers:read")),
) -> CustomerRead:
    service = CustomerService(db)
    customer = service.get_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("customers:write")),
) -> CustomerRead:
    service = CustomerService(db)
    customer = service.get_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    updated = service.update(customer, payload.model_dump(exclude_unset=True))
    return CustomerRead.model_validate(updated)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("customers:write")),
) -> None:
    service = CustomerService(db)
    customer = service.get_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    service.delete(customer)

@router.post("/{customer_id}/ai-summary")
async def generate_customer_summary(
    customer_id: int,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("insights:write")),
) -> dict[str, str]:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    activities = db.query(Activity).filter(Activity.customer_id == customer_id, Activity.deleted_at.is_(None)).all()
    deals = db.query(Deal).filter(Deal.customer_id == customer_id, Deal.deleted_at.is_(None)).all()
    service = InsightsService()
    summary = await service.summarize_customer(customer, activities, deals)
    return {"summary": summary}


@router.post("/{customer_id}/ai-insights")
async def generate_customer_insights(
    customer_id: int,
    db: Session = Depends(get_db),
    user: dict[str, str] = Depends(get_current_user_with_permission("insights:read")),
) -> dict[str, object]:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    activities = db.query(Activity).filter(Activity.customer_id == customer_id, Activity.deleted_at.is_(None)).all()
    deals = db.query(Deal).filter(Deal.customer_id == customer_id, Deal.deleted_at.is_(None)).all()
    service = InsightsService()
    insights = await service.build_insights(customer, activities, deals)
    return insights
