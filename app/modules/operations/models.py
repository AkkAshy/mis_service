"""
Operations Models
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class Surgery(Base):
    """Модель операции"""
    __tablename__ = "surgeries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    surgeon_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # Хирург

    # Информация об операции
    operation_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Название операции
    operation_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)  # Дата и время операции
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)  # Время начала
    end_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # Время окончания

    # Пребывание в палате
    pre_op_days: Mapped[int | None] = mapped_column(nullable=True)  # Дни в палате до операции
    post_op_days: Mapped[int | None] = mapped_column(nullable=True)  # Дни в палате после операции

    # Дополнительная информация
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # Примечания
    complications: Mapped[str | None] = mapped_column(Text, nullable=True)  # Осложнения
    outcome: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Исход операции

    # Динамические поля (JSON для дополнительных данных)
    additional_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Дополнительные динамические данные

    # Системные поля
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="surgeries")
    surgeon = relationship("User", foreign_keys=[surgeon_id], backref="surgeries_performed")
    creator = relationship("User", foreign_keys=[created_by], backref="surgeries_created")

    def __repr__(self):
        return f"<Surgery(id={self.id}, patient_id={self.patient_id}, operation_name={self.operation_name})>"