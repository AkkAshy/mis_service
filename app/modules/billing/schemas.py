"""
Billing Schemas (Pydantic)
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# TODO: Определить схемы для модуля billing
# Пример:
# class BillingBase(BaseModel):
#     name: str
#
# class BillingCreate(BillingBase):
#     pass
#
# class BillingUpdate(BillingBase):
#     pass
#
# class Billing(BillingBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     
#     class Config:
#         from_attributes = True
