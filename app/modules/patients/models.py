"""
Patients Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class Gender(str, enum.Enum):
    """Пол пациента"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodType(str, enum.Enum):
    """Группа крови"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class Patient(Base):
    """Модель пациента"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Медицинская информация
    blood_type = Column(Enum(BloodType), nullable=True)
    allergies = Column(Text, nullable=True)  # Аллергии
    chronic_diseases = Column(Text, nullable=True)  # Хронические заболевания
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    # Системные поля
    is_active = Column(String(1), default="Y", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def full_name(self) -> str:
        """Полное имя пациента"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.insert(1, self.middle_name)
        return " ".join(parts)

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.full_name})>"
