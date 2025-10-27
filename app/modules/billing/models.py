"""
Billing Models
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"), nullable=True)
    prescription_id: Mapped[int | None] = mapped_column(ForeignKey("prescriptions.id"), nullable=True)

    # Информация о счете
    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)  # Сумма счета
    status: Mapped[BillingStatus] = mapped_column(Enum(BillingStatus), default=BillingStatus.PENDING, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Описание услуги

    # Дата оплаты
    payment_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Системные поля
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="billing_records")
    appointment = relationship("Appointment", backref="billing")
    prescription = relationship("Prescription", backref="billing")
    creator = relationship("User", backref="created_billing")

    def __repr__(self):
        return f"<Billing(id={self.id}, patient_id={self.patient_id}, amount={self.amount}, status={self.status})>"
