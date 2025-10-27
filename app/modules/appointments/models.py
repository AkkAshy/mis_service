"""
Appointments Models
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Информация о записи
    appointment_type: Mapped[AppointmentType] = mapped_column(Enum(AppointmentType), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)

    # Дата и время
    scheduled_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(default=30, nullable=False)  # Продолжительность в минутах

    # Описание и заметки
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Причина обращения
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)          # Заметки врача
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)       # Симптомы

    # Системные поля
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # Кто создал запись
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")
    creator = relationship("User", foreign_keys=[created_by], backref="created_appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status={self.status})>"
