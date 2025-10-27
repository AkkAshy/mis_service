"""
Billing Schemas (Pydantic)
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class BillingBase(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    prescription_id: Optional[int] = None
    amount: Decimal
    description: Optional[str] = None


class BillingCreate(BillingBase):
    pass


class BillingUpdate(BaseModel):
    status: Optional[str] = None
    payment_date: Optional[datetime] = None
    description: Optional[str] = None


class Billing(BillingBase):
    id: int
    status: str
    payment_date: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
