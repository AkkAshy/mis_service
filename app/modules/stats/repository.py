"""
Stats Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from typing import List, Optional, Dict, Any, Sequence
from datetime import datetime, timedelta
from .models import SystemStats, DashboardStats
from .schemas import StatType


class StatsRepository:
    """Repository для работы со статистикой"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # SystemStats методы
    async def get_system_stat(self, stat_type: StatType, stat_key: str) -> Optional[SystemStats]:
        """Получить системную статистику по типу и ключу"""
        result = await self.db.execute(
            select(SystemStats).filter(
                and_(SystemStats.stat_type == stat_type, SystemStats.stat_key == stat_key)
            )
        )
        return result.scalar_one_or_none()

    async def get_system_stats_by_type(self, stat_type: StatType) -> Sequence[SystemStats]:
        """Получить все системные статистики по типу"""
        result = await self.db.execute(
            select(SystemStats).filter(SystemStats.stat_type == stat_type)
        )
        return result.scalars().all()

    async def create_or_update_system_stat(
        self,
        stat_type: StatType,
        stat_key: str,
        int_value: Optional[int] = None,
        float_value: Optional[float] = None,
        text_value: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> SystemStats:
        """Создать или обновить системную статистику"""
        # Ищем существующую запись
        existing = await self.get_system_stat(stat_type, stat_key)

        if existing:
            # Обновляем существующую
            if int_value is not None:
                existing.int_value = int_value
            if float_value is not None:
                existing.float_value = float_value
            if text_value is not None:
                existing.text_value = text_value
            if period_start is not None:
                existing.period_start = period_start
            if period_end is not None:
                existing.period_end = period_end
            if description is not None:
                existing.description = description
            return existing
        else:
            # Создаем новую
            stat = SystemStats(
                stat_type=stat_type,
                stat_key=stat_key,
                int_value=int_value,
                float_value=float_value,
                text_value=text_value,
                period_start=period_start,
                period_end=period_end,
                description=description
            )
            self.db.add(stat)
            await self.db.commit()
            await self.db.refresh(stat)
            return stat

    async def delete_system_stat(self, stat_type: StatType, stat_key: str) -> bool:
        """Удалить системную статистику"""
        stat = await self.get_system_stat(stat_type, stat_key)
        if stat:
            await self.db.delete(stat)
            await self.db.commit()
            return True
        return False

    # DashboardStats методы
    async def get_dashboard_stats(self, active_only: bool = True) -> Sequence[DashboardStats]:
        """Получить статистику дашборда"""
        query = select(DashboardStats).order_by(DashboardStats.position)
        if active_only:
            query = query.filter(DashboardStats.is_active == "Y")
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_dashboard_stat_by_id(self, stat_id: int) -> Optional[DashboardStats]:
        """Получить статистику дашборда по ID"""
        result = await self.db.execute(select(DashboardStats).filter(DashboardStats.id == stat_id))
        return result.scalar_one_or_none()

    async def create_dashboard_stat(self, dashboard_stat: DashboardStats) -> DashboardStats:
        """Создать статистику дашборда"""
        self.db.add(dashboard_stat)
        await self.db.commit()
        await self.db.refresh(dashboard_stat)
        return dashboard_stat

    async def update_dashboard_stat(self, dashboard_stat: DashboardStats) -> DashboardStats:
        """Обновить статистику дашборда"""
        await self.db.commit()
        await self.db.refresh(dashboard_stat)
        return dashboard_stat

    async def delete_dashboard_stat(self, stat_id: int) -> bool:
        """Удалить статистику дашборда"""
        stat = await self.get_dashboard_stat_by_id(stat_id)
        if stat:
            await self.db.delete(stat)
            await self.db.commit()
            return True
        return False

    # Агрегированные запросы для статистики
    async def get_user_stats(self) -> Dict[str, int]:
        """Получить статистику пользователей"""
        from app.modules.auth.models import User

        # Общее количество пользователей
        result = await self.db.execute(select(func.count(User.id)))
        total_users = result.scalar()

        # Активных пользователей
        result = await self.db.execute(select(func.count(User.id)).filter(User.is_active == "Y"))
        active_users = result.scalar()

        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0
        }

    async def get_patient_stats(self) -> Dict[str, int]:
        """Получить статистику пациентов"""
        from app.modules.patients.models import Patient

        # Общее количество пациентов
        result = await self.db.execute(select(func.count(Patient.id)))
        total_patients = result.scalar()

        # Активных пациентов
        result = await self.db.execute(select(func.count(Patient.id)).filter(Patient.is_active == "Y"))
        active_patients = result.scalar()

        return {
            "total_patients": total_patients or 0,
            "active_patients": active_patients or 0
        }

    async def get_appointment_stats(self) -> Dict[str, int]:
        """Получить статистику записей"""
        from app.modules.appointments.models import Appointment

        # Общее количество записей
        result = await self.db.execute(select(func.count(Appointment.id)))
        total_appointments = result.scalar()

        # Предстоящих записей
        now = datetime.utcnow()
        result = await self.db.execute(
            select(func.count(Appointment.id)).filter(Appointment.scheduled_date >= now)
        )
        upcoming_appointments = result.scalar()

        return {
            "total_appointments": total_appointments or 0,
            "upcoming_appointments": upcoming_appointments or 0
        }

    async def get_visit_stats(self, days: int = 30) -> Dict[str, int]:
        """Получить статистику визитов"""
        from app.modules.visits.models import Visit

        # Общее количество визитов
        result = await self.db.execute(select(func.count(Visit.id)))
        total_visits = result.scalar()

        # Недавних визитов
        start_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(Visit.id)).filter(Visit.visit_date >= start_date)
        )
        recent_visits = result.scalar()

        return {
            "total_visits": total_visits or 0,
            "recent_visits": recent_visits or 0
        }

    async def get_prescription_stats(self) -> Dict[str, int]:
        """Получить статистику рецептов"""
        from app.modules.prescriptions.models import Prescription

        result = await self.db.execute(select(func.count(Prescription.id)))
        total_prescriptions = result.scalar()

        return {"total_prescriptions": total_prescriptions or 0}

    async def get_surgery_stats(self, days: int = 30) -> Dict[str, int]:
        """Получить статистику операций"""
        from app.modules.operations.models import Surgery

        # Общее количество операций
        result = await self.db.execute(select(func.count(Surgery.id)))
        total_surgeries = result.scalar()

        # Недавних операций
        start_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(Surgery.id)).filter(Surgery.operation_date >= start_date)
        )
        recent_surgeries = result.scalar()

        return {
            "total_surgeries": total_surgeries or 0,
            "recent_surgeries": recent_surgeries or 0
        }

    async def get_monthly_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Получить месячную статистику"""
        from app.modules.patients.models import Patient
        from app.modules.appointments.models import Appointment
        from app.modules.visits.models import Visit
        from app.modules.operations.models import Surgery

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Статистика пациентов
        result = await self.db.execute(
            select(func.count(Patient.id)).filter(Patient.created_at.between(start_date, end_date))
        )
        patients_count = result.scalar()

        # Статистика записей
        result = await self.db.execute(
            select(func.count(Appointment.id)).filter(Appointment.created_at.between(start_date, end_date))
        )
        appointments_count = result.scalar()

        # Статистика визитов
        result = await self.db.execute(
            select(func.count(Visit.id)).filter(Visit.visit_date.between(start_date, end_date))
        )
        visits_count = result.scalar()

        # Статистика операций
        result = await self.db.execute(
            select(func.count(Surgery.id)).filter(Surgery.created_at.between(start_date, end_date))
        )
        surgeries_count = result.scalar()

        return {
            "month": f"{month:02d}",
            "year": year,
            "patients_count": patients_count or 0,
            "appointments_count": appointments_count or 0,
            "visits_count": visits_count or 0,
            "surgeries_count": surgeries_count or 0
        }
