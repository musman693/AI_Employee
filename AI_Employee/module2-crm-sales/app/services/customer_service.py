from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: dict[str, Any]) -> Customer:
        customer = Customer(**payload)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def list(self, skip: int = 0, limit: int = 20, search: str | None = None) -> tuple[list[Customer], int]:
        query = self.db.query(Customer).filter(Customer.deleted_at.is_(None))
        if search:
            query = query.filter(Customer.name.ilike(f"%{search}%"))
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def update(self, customer: Customer, payload: dict[str, Any]) -> Customer:
        for key, value in payload.items():
            setattr(customer, key, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        customer.deleted_at = customer.deleted_at or __import__("datetime").datetime.utcnow()
        customer.is_active = False
        self.db.commit()

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.scalar(select(Customer).where(Customer.email == email, Customer.deleted_at.is_(None)))
