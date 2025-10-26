"""
Prescriptions Schemas (Pydantic)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models import PrescriptionStatus


class MedicationBase(BaseModel):
    """Базовая схема лекарственного препарата"""
    medication_name: str = Field(..., min_length=1, max_length=255, description="Название препарата")
    generic_name: Optional[str] = Field(None, max_length=255, description="Международное название")
    dosage_form: Optional[str] = Field(None, max_length=100, description="Форма выпуска")
    strength: Optional[str] = Field(None, max_length=100, description="Дозировка")
    dosage: str = Field(..., min_length=1, max_length=100, description="Дозировка на прием")
    frequency: str = Field(..., min_length=1, max_length=100, description="Частота приема")
    duration_days: int = Field(..., ge=1, le=365, description="Продолжительность в днях")
    instructions: Optional[str] = Field(None, description="Инструкции по применению")
    quantity: int = Field(..., ge=1, description="Количество единиц")


class Medication(MedicationBase):
    """Полная схема лекарственного препарата"""
    id: int
    prescription_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PrescriptionBase(BaseModel):
    """Базовая схема рецепта"""
    patient_id: int = Field(..., description="ID пациента")
    doctor_id: int = Field(..., description="ID врача")
    visit_id: Optional[int] = Field(None, description="ID визита")
    notes: Optional[str] = Field(None, description="Заметки врача")
    follow_up_date: Optional[datetime] = Field(None, description="Дата следующего визита")


class PrescriptionCreate(PrescriptionBase):
    """Схема для создания рецепта"""
    medications: List[MedicationBase] = Field(..., min_length=1, description="Список препаратов")


class PrescriptionUpdate(BaseModel):
    """Схема для обновления рецепта"""
    status: Optional[PrescriptionStatus] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class Prescription(PrescriptionBase):
    """Полная схема рецепта"""
    id: int
    status: PrescriptionStatus
    prescription_date: datetime
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Связанные данные
    medications: List[Medication] = Field(default_factory=list)

    # Дополнительная информация
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True


class PrescriptionSummary(BaseModel):
    """Краткая информация о рецепте"""
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    status: PrescriptionStatus
    prescription_date: datetime
    medications_count: int = Field(default=0, description="Количество препаратов")

    class Config:
        from_attributes = True
