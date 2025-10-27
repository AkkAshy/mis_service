"""
Prescriptions Models
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class PrescriptionStatus(str, enum.Enum):
    """Статус рецепта"""
    ACTIVE = "active"        # Активный
    COMPLETED = "completed"  # Завершен
    CANCELLED = "cancelled"  # Отменен
    EXPIRED = "expired"      # Просрочен


class Medication(Base):
    """Модель лекарственного препарата"""
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.id"), nullable=False)

    # Информация о препарате
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    generic_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Международное название
    dosage_form: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Форма выпуска (таблетки, сироп и т.д.)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)     # Дозировка (500mg, 10ml и т.д.)

    # Дозировка и применение
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)     # Дозировка на прием
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)  # Частота приема
    duration_days: Mapped[int] = mapped_column(nullable=False)  # Продолжительность в днях

    # Инструкции
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)       # Инструкции по применению
    quantity: Mapped[int] = mapped_column(nullable=False)       # Количество единиц

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Prescription(Base):
    """Модель рецепта"""
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    visit_id: Mapped[int | None] = mapped_column(ForeignKey("visits.id"), nullable=True)

    # Информация о рецепте
    status: Mapped[PrescriptionStatus] = mapped_column(Enum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE, nullable=False)
    prescription_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Дополнительная информация
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # Заметки врача
    follow_up_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата следующего визита

    # Системные поля
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_prescriptions")
    visit = relationship("Visit", backref="prescription")
    creator = relationship("User", foreign_keys=[created_by], backref="created_prescriptions")

    # Связанные данные
    medications = relationship("Medication", backref="prescription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prescription(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status={self.status})>"
