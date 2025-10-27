"""
Patients Models
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Date, Enum
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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Медицинская информация
    blood_type: Mapped[BloodType | None] = mapped_column(Enum(BloodType), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)  # Аллергии
    chronic_diseases: Mapped[str | None] = mapped_column(Text, nullable=True)  # Хронические заболевания
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Системные поля
    is_active: Mapped[str] = mapped_column(String(1), default="Y", nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    @property
    def full_name(self) -> str:
        """Полное имя пациента"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.insert(1, self.middle_name)
        return " ".join(parts)

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.full_name})>"
