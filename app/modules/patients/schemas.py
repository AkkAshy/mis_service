"""
Patients Schemas (Pydantic)
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional
from .models import Gender, BloodType


class PatientBase(BaseModel):
    """Базовая схема пациента"""
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия")
    middle_name: Optional[str] = Field(None, max_length=50, description="Отчество")
    date_of_birth: date = Field(..., description="Дата рождения")
    gender: Gender = Field(..., description="Пол")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    email: Optional[EmailStr] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Адрес")

    # Медицинская информация
    blood_type: Optional[BloodType] = Field(None, description="Группа крови")
    allergies: Optional[str] = Field(None, description="Аллергии")
    chronic_diseases: Optional[str] = Field(None, description="Хронические заболевания")
    emergency_contact_name: Optional[str] = Field(None, max_length=100, description="Контактное лицо для экстренных случаев")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Телефон контактного лица")


class PatientCreate(PatientBase):
    """Схема для создания пациента"""
    pass


class PatientUpdate(BaseModel):
    """Схема для обновления пациента"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class Patient(PatientBase):
    """Полная схема пациента"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientSummary(BaseModel):
    """Краткая информация о пациенте"""
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: date
    phone: Optional[str] = None
    is_active: bool

    @property
    def full_name(self) -> str:
        """Полное имя пациента"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.insert(1, self.middle_name)
        return " ".join(parts)

    class Config:
        from_attributes = True
