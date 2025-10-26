"""
Prescriptions Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)

    # Информация о препарате
    medication_name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=True)  # Международное название
    dosage_form = Column(String(100), nullable=True)  # Форма выпуска (таблетки, сироп и т.д.)
    strength = Column(String(100), nullable=True)     # Дозировка (500mg, 10ml и т.д.)

    # Дозировка и применение
    dosage = Column(String(100), nullable=False)     # Дозировка на прием
    frequency = Column(String(100), nullable=False)  # Частота приема
    duration_days = Column(Integer, nullable=False)  # Продолжительность в днях

    # Инструкции
    instructions = Column(Text, nullable=True)       # Инструкции по применению
    quantity = Column(Integer, nullable=False)       # Количество единиц

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Prescription(Base):
    """Модель рецепта"""
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)

    # Информация о рецепте
    status = Column(Enum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE, nullable=False)
    prescription_date = Column(DateTime(timezone=True), server_default=func.now())

    # Дополнительная информация
    notes = Column(Text, nullable=True)  # Заметки врача
    follow_up_date = Column(DateTime(timezone=True), nullable=True)  # Дата следующего визита

    # Системные поля
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_prescriptions")
    visit = relationship("Visit", backref="prescription")
    creator = relationship("User", foreign_keys=[created_by], backref="created_prescriptions")

    # Связанные данные
    medications = relationship("Medication", backref="prescription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prescription(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status={self.status})>"
