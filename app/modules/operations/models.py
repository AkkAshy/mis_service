"""
Operations Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Date, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Surgery(Base):
    """Модель операции"""
    __tablename__ = "surgeries"

    id = Column(Integer, primary_key=True, index=True)

    # Связи
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    surgeon_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Хирург

    # Информация об операции
    operation_name = Column(String(255), nullable=False)  # Название операции
    operation_date = Column(DateTime(timezone=True), nullable=False)  # Дата и время операции
    start_time = Column(DateTime(timezone=True), nullable=False)  # Время начала
    end_time = Column(DateTime(timezone=True), nullable=True)  # Время окончания

    # Пребывание в палате
    pre_op_days = Column(Integer, nullable=True)  # Дни в палате до операции
    post_op_days = Column(Integer, nullable=True)  # Дни в палате после операции

    # Дополнительная информация
    notes = Column(Text, nullable=True)  # Примечания
    complications = Column(Text, nullable=True)  # Осложнения
    outcome = Column(String(100), nullable=True)  # Исход операции

    # Динамические поля (JSON для дополнительных данных)
    additional_data = Column(JSON, nullable=True)  # Дополнительные динамические данные

    # Системные поля
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    patient = relationship("Patient", backref="surgeries")
    surgeon = relationship("User", foreign_keys=[surgeon_id], backref="surgeries_performed")
    creator = relationship("User", foreign_keys=[created_by], backref="surgeries_created")

    def __repr__(self):
        return f"<Surgery(id={self.id}, patient_id={self.patient_id}, operation_name={self.operation_name})>"