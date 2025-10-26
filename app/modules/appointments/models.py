"""
Appointments Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, DateTime as DT, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class AppointmentStatus(str, enum.Enum):
    """Статус записи"""
    SCHEDULED = "scheduled"      # Запланирована
    CONFIRMED = "confirmed"      # Подтверждена
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"      # Завершена
    CANCELLED = "cancelled"      # Отменена
    NO_SHOW = "no_show"          # Пациент не пришел


class AppointmentType(str, enum.Enum):
    """Тип записи"""
    CONSULTATION = "consultation"    # Консультация
    EXAMINATION = "examination"      # Осмотр
    PROCEDURE = "procedure"          # Процедура
    SURGERY = "surgery"             # Операция
    FOLLOW_UP = "follow_up"         # Повторный прием
    EMERGENCY = "emergency"         # Экстренный случай


class Appointment(Base):
    """Модель записи на прием"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Информация о записи
    appointment_type = Column(Enum(AppointmentType), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)

    # Дата и время
    scheduled_date = Column(DT(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30, nullable=False)  # Продолжительность в минутах

    # Описание и заметки
    reason = Column(String(255), nullable=True)  # Причина обращения
    notes = Column(Text, nullable=True)          # Заметки врача
    symptoms = Column(Text, nullable=True)       # Симптомы

    # Системные поля
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Кто создал запись
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")
    creator = relationship("User", foreign_keys=[created_by], backref="created_appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status={self.status})>"
