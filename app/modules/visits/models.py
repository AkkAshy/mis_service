"""
Visits Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)

    # Диагноз по МКБ-10
    icd_code = Column(String(10), nullable=False)  # Код по МКБ-10
    diagnosis_name = Column(String(255), nullable=False)
    is_primary = Column(String(1), default="Y", nullable=False)  # Основной диагноз Y/N

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Treatment(Base):
    """Модель лечения"""
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)

    # Лечение
    treatment_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=True)  # Дозировка
    frequency = Column(String(100), nullable=True)  # Частота приема
    duration_days = Column(Integer, nullable=True)  # Продолжительность в днях

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VitalSigns(Base):
    """Модель жизненных показателей"""
    __tablename__ = "vital_signs"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)

    # Жизненные показатели
    blood_pressure_systolic = Column(Integer, nullable=True)  # Систолическое давление
    blood_pressure_diastolic = Column(Integer, nullable=True)  # Диастолическое давление
    heart_rate = Column(Integer, nullable=True)  # ЧСС
    temperature = Column(Float, nullable=True)  # Температура
    weight = Column(Float, nullable=True)  # Вес
    height = Column(Float, nullable=True)  # Рост
    bmi = Column(Float, nullable=True)  # ИМТ

    measured_at = Column(DateTime(timezone=True), server_default=func.now())


class Visit(Base):
    """Модель визита пациента"""
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)

    # Информация о визите
    status = Column(Enum(VisitStatus), default=VisitStatus.SCHEDULED, nullable=False)
    visit_date = Column(DateTime(timezone=True), nullable=False)

    # Анамнез и осмотр
    chief_complaint = Column(Text, nullable=True)  # Основная жалоба
    history_of_present_illness = Column(Text, nullable=True)  # История настоящего заболевания
    physical_examination = Column(Text, nullable=True)  # Физикальный осмотр
    assessment = Column(Text, nullable=True)  # Оценка состояния
    plan = Column(Text, nullable=True)  # План лечения

    # Системные поля
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
