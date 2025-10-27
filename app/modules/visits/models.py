"""
Visits Models
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class VisitStatus(str, enum.Enum):
    """Статус визита"""
    SCHEDULED = "scheduled"      # Запланирован
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"      # Завершен
    CANCELLED = "cancelled"      # Отменен


class Diagnosis(Base):
    """Модель диагноза"""
    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), nullable=False)

    # Диагноз по МКБ-10
    icd_code: Mapped[str] = mapped_column(String(10), nullable=False)  # Код по МКБ-10
    diagnosis_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[str] = mapped_column(String(1), default="Y", nullable=False)  # Основной диагноз Y/N

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Treatment(Base):
    """Модель лечения"""
    __tablename__ = "treatments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), nullable=False)

    # Лечение
    treatment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Дозировка
    frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Частота приема
    duration_days: Mapped[int | None] = mapped_column(nullable=True)  # Продолжительность в днях

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class VitalSigns(Base):
    """Модель жизненных показателей"""
    __tablename__ = "vital_signs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), nullable=False)

    # Жизненные показатели
    blood_pressure_systolic: Mapped[int | None] = mapped_column(nullable=True)  # Систолическое давление
    blood_pressure_diastolic: Mapped[int | None] = mapped_column(nullable=True)  # Диастолическое давление
    heart_rate: Mapped[int | None] = mapped_column(nullable=True)  # ЧСС
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)  # Температура
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)  # Вес
    height: Mapped[float | None] = mapped_column(Float, nullable=True)  # Рост
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)  # ИМТ

    measured_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Visit(Base):
    """Модель визита пациента"""
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"), nullable=True)

    # Информация о визите
    status: Mapped[VisitStatus] = mapped_column(Enum(VisitStatus), default=VisitStatus.SCHEDULED, nullable=False)
    visit_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Анамнез и осмотр
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)  # Основная жалоба
    history_of_present_illness: Mapped[str | None] = mapped_column(Text, nullable=True)  # История настоящего заболевания
    physical_examination: Mapped[str | None] = mapped_column(Text, nullable=True)  # Физикальный осмотр
    assessment: Mapped[str | None] = mapped_column(Text, nullable=True)  # Оценка состояния
    plan: Mapped[str | None] = mapped_column(Text, nullable=True)  # План лечения

    # Системные поля
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="visits")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_visits")
    appointment = relationship("Appointment", backref="visit")
    creator = relationship("User", foreign_keys=[created_by], backref="created_visits")

    # Связанные данные
    diagnoses = relationship("Diagnosis", backref="visit", cascade="all, delete-orphan")
    treatments = relationship("Treatment", backref="visit", cascade="all, delete-orphan")
    vital_signs = relationship("VitalSigns", backref="visit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Visit(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status={self.status})>"
