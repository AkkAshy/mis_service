"""
Stats Schemas (Pydantic)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class StatType(str, Enum):
    """Типы статистики"""
    USERS = "users"
    PATIENTS = "patients"
    APPOINTMENTS = "appointments"
    VISITS = "visits"
    PRESCRIPTIONS = "prescriptions"
    SURGERIES = "surgeries"
    BILLING = "billing"


class SystemStatsBase(BaseModel):
    """Базовая схема системной статистики"""
    stat_type: StatType = Field(..., description="Тип статистики")
    stat_key: str = Field(..., min_length=1, max_length=100, description="Ключ статистики")
    int_value: Optional[int] = Field(None, description="Целочисленное значение")
    float_value: Optional[float] = Field(None, description="Дробное значение")
    text_value: Optional[str] = Field(None, description="Текстовое значение")
    period_start: Optional[datetime] = Field(None, description="Начало периода")
    period_end: Optional[datetime] = Field(None, description="Конец периода")
    description: Optional[str] = Field(None, max_length=255, description="Описание")


class SystemStatsCreate(SystemStatsBase):
    """Схема для создания системной статистики"""
    pass


class SystemStatsUpdate(BaseModel):
    """Схема для обновления системной статистики"""
    int_value: Optional[int] = None
    float_value: Optional[float] = None
    text_value: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=255)


class SystemStats(SystemStatsBase):
    """Полная схема системной статистики"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DashboardStatsBase(BaseModel):
    """Базовая схема статистики дашборда"""
    widget_type: str = Field(..., min_length=1, max_length=50, description="Тип виджета")
    widget_name: str = Field(..., min_length=1, max_length=100, description="Название виджета")
    data: str = Field(..., description="Данные виджета (JSON)")
    position: int = Field(default=0, ge=0, description="Порядок отображения")
    is_active: bool = Field(default=True, description="Активен ли виджет")


class DashboardStatsCreate(DashboardStatsBase):
    """Схема для создания статистики дашборда"""
    pass


class DashboardStatsUpdate(BaseModel):
    """Схема для обновления статистики дашборда"""
    widget_name: Optional[str] = Field(None, min_length=1, max_length=100)
    data: Optional[str] = None
    position: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class DashboardStats(DashboardStatsBase):
    """Полная схема статистики дашборда"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatsSummary(BaseModel):
    """Сводная статистика системы"""
    total_users: int = Field(default=0, description="Общее количество пользователей")
    active_users: int = Field(default=0, description="Активных пользователей")
    total_patients: int = Field(default=0, description="Общее количество пациентов")
    active_patients: int = Field(default=0, description="Активных пациентов")
    total_appointments: int = Field(default=0, description="Общее количество записей")
    upcoming_appointments: int = Field(default=0, description="Предстоящих записей")
    total_visits: int = Field(default=0, description="Общее количество визитов")
    recent_visits: int = Field(default=0, description="Недавних визитов")
    total_prescriptions: int = Field(default=0, description="Общее количество рецептов")
    total_surgeries: int = Field(default=0, description="Общее количество операций")
    recent_surgeries: int = Field(default=0, description="Недавних операций")


class ChartData(BaseModel):
    """Данные для графиков"""
    labels: List[str] = Field(..., description="Метки")
    datasets: List[Dict[str, Any]] = Field(..., description="Наборы данных")


class MonthlyStats(BaseModel):
    """Месячная статистика"""
    month: str = Field(..., description="Месяц")
    year: int = Field(..., description="Год")
    patients_count: int = Field(default=0, description="Количество пациентов")
    appointments_count: int = Field(default=0, description="Количество записей")
    visits_count: int = Field(default=0, description="Количество визитов")
    surgeries_count: int = Field(default=0, description="Количество операций")
