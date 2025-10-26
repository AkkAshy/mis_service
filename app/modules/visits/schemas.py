"""
Visits Schemas (Pydantic)
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# TODO: Определить схемы для модуля visits
# Пример:
# class VisitsBase(BaseModel):
#     name: str
#
# class VisitsCreate(VisitsBase):
#     pass
#
# class VisitsUpdate(VisitsBase):
#     pass
#
# class Visits(VisitsBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     
#     class Config:
#         from_attributes = True
