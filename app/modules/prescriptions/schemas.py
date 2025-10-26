"""
Prescriptions Schemas (Pydantic)
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# TODO: Определить схемы для модуля prescriptions
# Пример:
# class PrescriptionsBase(BaseModel):
#     name: str
#
# class PrescriptionsCreate(PrescriptionsBase):
#     pass
#
# class PrescriptionsUpdate(PrescriptionsBase):
#     pass
#
# class Prescriptions(PrescriptionsBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     
#     class Config:
#         from_attributes = True
