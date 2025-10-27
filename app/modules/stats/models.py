"""
Stats Models
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.db.session import Base


class SystemStats(Base):
    """Модель для системной статистики"""
    __tablename__ = "system_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Тип статистики
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # users, patients, appointments, etc.
    stat_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # total, active, monthly, etc.

    # Значения
    int_value: Mapped[int | None] = mapped_column(nullable=True)  # Целочисленное значение
    float_value: Mapped[float | None] = mapped_column(Float, nullable=True)  # Дробное значение
    text_value: Mapped[str | None] = mapped_column(Text, nullable=True)  # Текстовое значение

    # Период статистики
    period_start: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Метаданные
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Системные поля
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SystemStats(type={self.stat_type}, key={self.stat_key}, value={self.int_value or self.float_value or self.text_value})>"


class DashboardStats(Base):
    """Модель для статистики дашборда"""
    __tablename__ = "dashboard_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Тип виджета
    widget_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # chart, counter, table, etc.
    widget_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Данные виджета (JSON)
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON строка с данными

    # Настройки отображения
    position: Mapped[int] = mapped_column(default=0)  # Порядок отображения
    is_active: Mapped[str] = mapped_column(String(1), default="Y", nullable=False)

    # Системные поля
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DashboardStats(widget={self.widget_name}, type={self.widget_type})>"
