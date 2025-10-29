"""
Appointments Schemas (Pydantic)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import AppointmentStatus, AppointmentType


class AppointmentBase(BaseModel):
    """Базовая схема записи на прием"""
    patient_id: int = Field(..., description="ID пациента")
    doctor_id: int = Field(..., description="ID врача")
    appointment_type: AppointmentType = Field(..., description="Тип приема")
    scheduled_date: datetime = Field(..., description="Дата и время приема")
    duration_minutes: int = Field(default=30, ge=5, le=480, description="Продолжительность в минутах")
    reason: Optional[str] = Field(None, max_length=255, description="Причина обращения")
    notes: Optional[str] = Field(None, description="Заметки врача")
    symptoms: Optional[str] = Field(None, description="Симптомы")


class AppointmentCreate(AppointmentBase):
    """Схема для создания записи"""
    pass


class AppointmentUpdate(BaseModel):
    """Схема для обновления записи"""
    status: Optional[AppointmentStatus] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    reason: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    symptoms: Optional[str] = None


class Appointment(AppointmentBase):
    """Полная схема записи"""
    id: int
    status: AppointmentStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Дополнительная информация
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    visit_id: Optional[int] = None  # ID созданного визита

    class Config:
        from_attributes = True


class AppointmentSummary(BaseModel):
    """Краткая информация о записи"""
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    appointment_type: AppointmentType
    status: AppointmentStatus
    scheduled_date: datetime
    duration_minutes: int

    class Config:
        from_attributes = True
