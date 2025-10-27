"""
Stats Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.db.session import Base


class SystemStats(Base):
    """Модель для системной статистики"""
    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, index=True)

    # Тип статистики
    stat_type = Column(String(50), nullable=False, index=True)  # users, patients, appointments, etc.
    stat_key = Column(String(100), nullable=False, index=True)  # total, active, monthly, etc.

    # Значения
    int_value = Column(Integer, nullable=True)  # Целочисленное значение
    float_value = Column(Float, nullable=True)  # Дробное значение
    text_value = Column(Text, nullable=True)  # Текстовое значение

    # Период статистики
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # Метаданные
    description = Column(String(255), nullable=True)

    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SystemStats(type={self.stat_type}, key={self.stat_key}, value={self.int_value or self.float_value or self.text_value})>"


class DashboardStats(Base):
    """Модель для статистики дашборда"""
    __tablename__ = "dashboard_stats"

    id = Column(Integer, primary_key=True, index=True)

    # Тип виджета
    widget_type = Column(String(50), nullable=False, index=True)  # chart, counter, table, etc.
    widget_name = Column(String(100), nullable=False)

    # Данные виджета (JSON)
    data = Column(Text, nullable=False)  # JSON строка с данными

    # Настройки отображения
    position = Column(Integer, default=0)  # Порядок отображения
    is_active = Column(String(1), default="Y", nullable=False)

    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DashboardStats(widget={self.widget_name}, type={self.widget_type})>"
