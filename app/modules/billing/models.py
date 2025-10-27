"""
Billing Models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class BillingStatus(str, enum.Enum):
    """Статус счета"""
    PENDING = "pending"      # Ожидает оплаты
    PAID = "paid"            # Оплачен
    CANCELLED = "cancelled"  # Отменен
    OVERDUE = "overdue"      # Просрочен


class Billing(Base):
    """Модель счета"""
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)

    # Информация о счете
    amount = Column(Numeric(10, 2), nullable=False)  # Сумма счета
    status = Column(Enum(BillingStatus), default=BillingStatus.PENDING, nullable=False)
    description = Column(String(255), nullable=True)  # Описание услуги

    # Дата оплаты
    payment_date = Column(DateTime(timezone=True), nullable=True)

    # Системные поля
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="billing_records")
    appointment = relationship("Appointment", backref="billing")
    prescription = relationship("Prescription", backref="billing")
    creator = relationship("User", backref="created_billing")

    def __repr__(self):
        return f"<Billing(id={self.id}, patient_id={self.patient_id}, amount={self.amount}, status={self.status})>"
