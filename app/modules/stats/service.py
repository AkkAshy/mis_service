"""
Stats Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Sequence
from datetime import datetime
import json
from .repository import StatsRepository
from .models import SystemStats, DashboardStats
from .schemas import (
    StatType, SystemStatsCreate, SystemStatsUpdate,
    DashboardStatsCreate, DashboardStatsUpdate,
    StatsSummary, ChartData, MonthlyStats
)


class StatsService:
    """Сервис для бизнес-логики статистики"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = StatsRepository(db)

    # SystemStats методы
    async def get_system_stat(self, stat_type: StatType, stat_key: str) -> Optional[SystemStats]:
        """Получить системную статистику"""
        return await self.repository.get_system_stat(stat_type, stat_key)

    async def get_system_stats_by_type(self, stat_type: StatType) -> Sequence[SystemStats]:
        """Получить системные статистики по типу"""
        return await self.repository.get_system_stats_by_type(stat_type)

    async def create_system_stat(self, stat_data: SystemStatsCreate) -> SystemStats:
        """Создать системную статистику"""
        return await self.repository.create_or_update_system_stat(
            stat_type=stat_data.stat_type,
            stat_key=stat_data.stat_key,
            int_value=stat_data.int_value,
            float_value=stat_data.float_value,
            text_value=stat_data.text_value,
            period_start=stat_data.period_start,
            period_end=stat_data.period_end,
            description=stat_data.description
        )

    async def update_system_stat(
        self,
        stat_type: StatType,
        stat_key: str,
        stat_data: SystemStatsUpdate
    ) -> Optional[SystemStats]:
        """Обновить системную статистику"""
        existing = await self.repository.get_system_stat(stat_type, stat_key)
        if not existing:
            return None

        update_data = stat_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def delete_system_stat(self, stat_type: StatType, stat_key: str) -> bool:
        """Удалить системную статистику"""
        return await self.repository.delete_system_stat(stat_type, stat_key)

    # DashboardStats методы
    async def get_dashboard_stats(self, active_only: bool = True) -> Sequence[DashboardStats]:
        """Получить статистику дашборда"""
        return await self.repository.get_dashboard_stats(active_only)

    async def get_dashboard_stat(self, stat_id: int) -> Optional[DashboardStats]:
        """Получить статистику дашборда по ID"""
        return await self.repository.get_dashboard_stat_by_id(stat_id)

    async def create_dashboard_stat(self, stat_data: DashboardStatsCreate) -> DashboardStats:
        """Создать статистику дашборда"""
        dashboard_stat = DashboardStats(
            widget_type=stat_data.widget_type,
            widget_name=stat_data.widget_name,
            data=stat_data.data,
            position=stat_data.position,
            is_active="Y" if stat_data.is_active else "N"
        )
        return await self.repository.create_dashboard_stat(dashboard_stat)

    async def update_dashboard_stat(self, stat_id: int, stat_data: DashboardStatsUpdate) -> Optional[DashboardStats]:
        """Обновить статистику дашборда"""
        existing = await self.repository.get_dashboard_stat_by_id(stat_id)
        if not existing:
            return None

        update_data = stat_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "is_active":
                existing.is_active = "Y" if value else "N"
            else:
                setattr(existing, field, value)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing

    async def delete_dashboard_stat(self, stat_id: int) -> bool:
        """Удалить статистику дашборда"""
        return await self.repository.delete_dashboard_stat(stat_id)

    # Агрегированные методы статистики
    async def get_stats_summary(self) -> StatsSummary:
        """Получить сводную статистику системы"""
        user_stats = await self.repository.get_user_stats()
        patient_stats = await self.repository.get_patient_stats()
        appointment_stats = await self.repository.get_appointment_stats()
        visit_stats = await self.repository.get_visit_stats()
        prescription_stats = await self.repository.get_prescription_stats()
        surgery_stats = await self.repository.get_surgery_stats()

        return StatsSummary(
            total_users=user_stats["total_users"],
            active_users=user_stats["active_users"],
            total_patients=patient_stats["total_patients"],
            active_patients=patient_stats["active_patients"],
            total_appointments=appointment_stats["total_appointments"],
            upcoming_appointments=appointment_stats["upcoming_appointments"],
            total_visits=visit_stats["total_visits"],
            recent_visits=visit_stats["recent_visits"],
            total_prescriptions=prescription_stats["total_prescriptions"],
            total_surgeries=surgery_stats["total_surgeries"],
            recent_surgeries=surgery_stats["recent_surgeries"]
        )

    async def get_monthly_stats(self, year: int, months: int = 12) -> List[MonthlyStats]:
        """Получить месячную статистику за указанное количество месяцев"""
        stats = []
        current_date = datetime.now()

        for i in range(months):
            # Вычисляем год и месяц для i месяцев назад
            target_date = current_date.replace(day=1)  # Первый день текущего месяца

            # Отнимаем i месяцев
            for _ in range(i):
                if target_date.month == 1:
                    target_date = target_date.replace(year=target_date.year - 1, month=12)
                else:
                    target_date = target_date.replace(month=target_date.month - 1)

            month_stat = await self.repository.get_monthly_stats(target_date.year, target_date.month)
            stats.append(MonthlyStats(**month_stat))

        return list(reversed(stats))  # Возвращаем в хронологическом порядке

    async def get_patients_chart_data(self, months: int = 12) -> ChartData:
        """Получить данные для графика пациентов"""
        monthly_stats = await self.get_monthly_stats(datetime.now().year, months)

        labels = [f"{stat.month}.{stat.year}" for stat in monthly_stats]
        datasets = [{
            "label": "Новые пациенты",
            "data": [stat.patients_count for stat in monthly_stats],
            "borderColor": "rgb(75, 192, 192)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "tension": 0.1
        }]

        return ChartData(labels=labels, datasets=datasets)

    async def get_appointments_chart_data(self, months: int = 12) -> ChartData:
        """Получить данные для графика записей"""
        monthly_stats = await self.get_monthly_stats(datetime.now().year, months)

        labels = [f"{stat.month}.{stat.year}" for stat in monthly_stats]
        datasets = [{
            "label": "Новые записи",
            "data": [stat.appointments_count for stat in monthly_stats],
            "borderColor": "rgb(255, 99, 132)",
            "backgroundColor": "rgba(255, 99, 132, 0.2)",
            "tension": 0.1
        }]

        return ChartData(labels=labels, datasets=datasets)

    async def get_visits_chart_data(self, months: int = 12) -> ChartData:
        """Получить данные для графика визитов"""
        monthly_stats = await self.get_monthly_stats(datetime.now().year, months)

        labels = [f"{stat.month}.{stat.year}" for stat in monthly_stats]
        datasets = [{
            "label": "Визиты",
            "data": [stat.visits_count for stat in monthly_stats],
            "borderColor": "rgb(54, 162, 235)",
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "tension": 0.1
        }]

        return ChartData(labels=labels, datasets=datasets)

    async def get_surgeries_chart_data(self, months: int = 12) -> ChartData:
        """Получить данные для графика операций"""
        monthly_stats = await self.get_monthly_stats(datetime.now().year, months)

        labels = [f"{stat.month}.{stat.year}" for stat in monthly_stats]
        datasets = [{
            "label": "Операции",
            "data": [stat.surgeries_count for stat in monthly_stats],
            "borderColor": "rgb(255, 205, 86)",
            "backgroundColor": "rgba(255, 205, 86, 0.2)",
            "tension": 0.1
        }]

        return ChartData(labels=labels, datasets=datasets)

    async def update_cached_stats(self) -> None:
        """Обновить кэшированную статистику в базе данных"""
        summary = await self.get_stats_summary()

        # Обновляем системные статистики
        await self.repository.create_or_update_system_stat(
            StatType.USERS, "total", int_value=summary.total_users,
            description="Общее количество пользователей"
        )
        await self.repository.create_or_update_system_stat(
            StatType.USERS, "active", int_value=summary.active_users,
            description="Количество активных пользователей"
        )

        await self.repository.create_or_update_system_stat(
            StatType.PATIENTS, "total", int_value=summary.total_patients,
            description="Общее количество пациентов"
        )
        await self.repository.create_or_update_system_stat(
            StatType.PATIENTS, "active", int_value=summary.active_patients,
            description="Количество активных пациентов"
        )

        await self.repository.create_or_update_system_stat(
            StatType.APPOINTMENTS, "total", int_value=summary.total_appointments,
            description="Общее количество записей"
        )
        await self.repository.create_or_update_system_stat(
            StatType.APPOINTMENTS, "upcoming", int_value=summary.upcoming_appointments,
            description="Количество предстоящих записей"
        )

        await self.repository.create_or_update_system_stat(
            StatType.VISITS, "total", int_value=summary.total_visits,
            description="Общее количество визитов"
        )
        await self.repository.create_or_update_system_stat(
            StatType.VISITS, "recent", int_value=summary.recent_visits,
            description="Количество недавних визитов (30 дней)"
        )

        await self.repository.create_or_update_system_stat(
            StatType.PRESCRIPTIONS, "total", int_value=summary.total_prescriptions,
            description="Общее количество рецептов"
        )

        await self.repository.create_or_update_system_stat(
            StatType.SURGERIES, "total", int_value=summary.total_surgeries,
            description="Общее количество операций"
        )
        await self.repository.create_or_update_system_stat(
            StatType.SURGERIES, "recent", int_value=summary.recent_surgeries,
            description="Количество недавних операций (30 дней)"
        )
