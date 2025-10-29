"""
Visits Schemas (Pydantic)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models import VisitStatus


class VitalSignsBase(BaseModel):
    """Базовая схема жизненных показателей"""
    blood_pressure_systolic: Optional[int] = Field(None, ge=60, le=250, description="Систолическое давление")
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=150, description="Диастолическое давление")
    heart_rate: Optional[int] = Field(None, ge=30, le=200, description="ЧСС (удары в минуту)")
    temperature: Optional[float] = Field(None, ge=30.0, le=45.0, description="Температура (°C)")
    weight: Optional[float] = Field(None, ge=1.0, le=300.0, description="Вес (кг)")
    height: Optional[float] = Field(None, ge=30.0, le=250.0, description="Рост (см)")
    bmi: Optional[float] = Field(None, ge=5.0, le=70.0, description="ИМТ")
    oxygen_saturation: Optional[float] = Field(None, ge=50.0, le=100.0, description="Сатурация кислорода (%)")


class VitalSigns(VitalSignsBase):
    """Полная схема жизненных показателей"""
    id: int
    visit_id: int
    measured_at: datetime

    class Config:
        from_attributes = True


class DiagnosisBase(BaseModel):
    """Базовая схема диагноза"""
    icd_code: str = Field(..., min_length=1, max_length=10, description="Код по МКБ-10")
    diagnosis_name: str = Field(..., min_length=1, max_length=255, description="Название диагноза")
    is_primary: bool = Field(default=True, description="Основной диагноз")


class Diagnosis(DiagnosisBase):
    """Полная схема диагноза"""
    id: int
    visit_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TreatmentBase(BaseModel):
    """Базовая схема назначения лечения"""
    medication_name: str = Field(..., min_length=1, max_length=255, description="Название лекарства")
    dosage: str = Field(..., min_length=1, max_length=100, description="Дозировка")
    frequency: str = Field(..., min_length=1, max_length=100, description="Частота приема")
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="Продолжительность (дни)")
    instructions: Optional[str] = Field(None, description="Инструкции")


class Treatment(TreatmentBase):
    """Полная схема назначения лечения"""
    id: int
    visit_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VisitBase(BaseModel):
    """Базовая схема визита"""
    patient_id: int = Field(..., description="ID пациента")
    doctor_id: int = Field(..., description="ID врача")
    appointment_id: Optional[int] = Field(None, description="ID записи на прием")
    visit_date: datetime = Field(..., description="Дата и время визита")
    chief_complaint: Optional[str] = Field(None, description="Основная жалоба")
    history_of_present_illness: Optional[str] = Field(None, description="История настоящего заболевания")
    physical_examination: Optional[str] = Field(None, description="Физикальный осмотр")
    assessment: Optional[str] = Field(None, description="Оценка состояния")
    plan: Optional[str] = Field(None, description="План лечения")


class VisitCreate(VisitBase):
    """Схема для создания визита"""
    vital_signs: Optional[VitalSignsBase] = None
    diagnoses: Optional[List[DiagnosisBase]] = Field(default_factory=list)
    treatments: Optional[List[TreatmentBase]] = Field(default_factory=list)


class VisitUpdate(BaseModel):
    """Схема для обновления визита"""
    status: Optional[VisitStatus] = None
    visit_date: Optional[datetime] = None
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    physical_examination: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    vital_signs: Optional[VitalSignsBase] = None
    diagnoses: Optional[List[DiagnosisBase]] = Field(default_factory=list)
    treatments: Optional[List[TreatmentBase]] = Field(default_factory=list)


class Visit(VisitBase):
    """Полная схема визита"""
    id: int
    status: VisitStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Связанные данные
    vital_signs: Optional[VitalSigns] = None
    diagnoses: List[Diagnosis] = Field(default_factory=list)
    treatments: List[Treatment] = Field(default_factory=list)

    # Дополнительная информация
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

    class Config:
        from_attributes = True


class VisitSummary(BaseModel):
    """Краткая информация о визите"""
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    status: VisitStatus
    visit_date: datetime
    chief_complaint: Optional[str] = None

    class Config:
        from_attributes = True
