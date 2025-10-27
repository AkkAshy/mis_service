"""
Operations Schemas (Pydantic)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from app.modules.patients.schemas import PatientSummary


class SurgeryBase(BaseModel):
    """Базовая схема операции"""
    patient_id: int = Field(..., description="ID пациента")
    surgeon_id: int = Field(..., description="ID хирурга")
    operation_name: str = Field(..., min_length=1, max_length=255, description="Название операции")
    operation_date: datetime = Field(..., description="Дата и время операции")
    start_time: datetime = Field(..., description="Время начала операции")
    end_time: Optional[datetime] = Field(None, description="Время окончания операции")
    pre_op_days: Optional[int] = Field(None, ge=0, description="Дни в палате до операции")
    post_op_days: Optional[int] = Field(None, ge=0, description="Дни в палате после операции")
    notes: Optional[str] = Field(None, description="Примечания")
    complications: Optional[str] = Field(None, description="Осложнения")
    outcome: Optional[str] = Field(None, max_length=100, description="Исход операции")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные динамические данные")


class SurgeryCreate(SurgeryBase):
    """Схема для создания операции"""
    pass


class SurgeryUpdate(BaseModel):
    """Схема для обновления операции"""
    operation_name: Optional[str] = Field(None, min_length=1, max_length=255)
    operation_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pre_op_days: Optional[int] = Field(None, ge=0)
    post_op_days: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    complications: Optional[str] = None
    outcome: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None


class Surgery(SurgeryBase):
    """Полная схема операции"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Связанные данные
    patient: Optional[PatientSummary] = None

    class Config:
        from_attributes = True


class SurgerySummary(BaseModel):
    """Краткая информация об операции"""
    id: int
    patient_id: int
    operation_name: str
    operation_date: datetime
    start_time: datetime
    end_time: Optional[datetime] = None
    outcome: Optional[str] = None

    class Config:
        from_attributes = True