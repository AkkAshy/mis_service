"""
Stats Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from .service import StatsService
from .schemas import (
    StatType, SystemStats, SystemStatsCreate, SystemStatsUpdate,
    DashboardStats, DashboardStatsCreate, DashboardStatsUpdate,
    StatsSummary, ChartData, MonthlyStats
)

router = APIRouter()


@router.get("/summary", response_model=StatsSummary)
async def get_stats_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить сводную статистику системы"""
    service = StatsService(db)
    return await service.get_stats_summary()


@router.get("/monthly", response_model=List[MonthlyStats])
async def get_monthly_stats(
    months: int = Query(12, ge=1, le=24, description="Количество месяцев для статистики"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить месячную статистику"""
    service = StatsService(db)
    stats = await service.get_monthly_stats(datetime.now().year, months)
    return stats


@router.get("/charts/patients", response_model=ChartData)
async def get_patients_chart(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить данные для графика пациентов"""
    service = StatsService(db)
    return await service.get_patients_chart_data(months)


@router.get("/charts/appointments", response_model=ChartData)
async def get_appointments_chart(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить данные для графика записей"""
    service = StatsService(db)
    return await service.get_appointments_chart_data(months)


@router.get("/charts/visits", response_model=ChartData)
async def get_visits_chart(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить данные для графика визитов"""
    service = StatsService(db)
    return await service.get_visits_chart_data(months)


@router.get("/charts/surgeries", response_model=ChartData)
async def get_surgeries_chart(
    months: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить данные для графика операций"""
    service = StatsService(db)
    return await service.get_surgeries_chart_data(months)


# SystemStats эндпоинты
@router.get("/system", response_model=List[SystemStats])
async def get_system_stats(
    stat_type: Optional[StatType] = Query(None, description="Тип статистики"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить системную статистику"""
    service = StatsService(db)
    if stat_type:
        stats = await service.get_system_stats_by_type(stat_type)
        return list(stats)
    else:
        # Возвращаем все типы статистики
        all_stats = []
        for stat_type_enum in StatType:
            stats = await service.get_system_stats_by_type(stat_type_enum)
            all_stats.extend(stats)
        return all_stats


@router.get("/system/{stat_type}/{stat_key}", response_model=SystemStats)
async def get_system_stat(
    stat_type: StatType,
    stat_key: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить конкретную системную статистику"""
    service = StatsService(db)
    stat = await service.get_system_stat(stat_type, stat_key)
    if not stat:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Statistic not found")
    return stat


@router.post("/system", response_model=SystemStats)
async def create_system_stat(
    stat_data: SystemStatsCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Создать системную статистику"""
    service = StatsService(db)
    return await service.create_system_stat(stat_data)


@router.put("/system/{stat_type}/{stat_key}", response_model=SystemStats)
async def update_system_stat(
    stat_type: StatType,
    stat_key: str,
    stat_data: SystemStatsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Обновить системную статистику"""
    service = StatsService(db)
    updated_stat = await service.update_system_stat(stat_type, stat_key, stat_data)
    if not updated_stat:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Statistic not found")
    return updated_stat


@router.delete("/system/{stat_type}/{stat_key}")
async def delete_system_stat(
    stat_type: StatType,
    stat_key: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Удалить системную статистику"""
    service = StatsService(db)
    deleted = await service.delete_system_stat(stat_type, stat_key)
    if not deleted:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Statistic not found")
    return {"message": "Statistic deleted successfully"}


# DashboardStats эндпоинты
@router.get("/dashboard", response_model=List[DashboardStats])
async def get_dashboard_stats(
    active_only: bool = Query(True, description="Только активные виджеты"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить статистику дашборда"""
    service = StatsService(db)
    stats = await service.get_dashboard_stats(active_only)
    return list(stats)


@router.get("/dashboard/{stat_id}", response_model=DashboardStats)
async def get_dashboard_stat(
    stat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить статистику дашборда по ID"""
    service = StatsService(db)
    stat = await service.get_dashboard_stat(stat_id)
    if not stat:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Dashboard statistic not found")
    return stat


@router.post("/dashboard", response_model=DashboardStats)
async def create_dashboard_stat(
    stat_data: DashboardStatsCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Создать статистику дашборда"""
    service = StatsService(db)
    return await service.create_dashboard_stat(stat_data)


@router.put("/dashboard/{stat_id}", response_model=DashboardStats)
async def update_dashboard_stat(
    stat_id: int,
    stat_data: DashboardStatsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Обновить статистику дашборда"""
    service = StatsService(db)
    updated_stat = await service.update_dashboard_stat(stat_id, stat_data)
    if not updated_stat:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Dashboard statistic not found")
    return updated_stat


@router.delete("/dashboard/{stat_id}")
async def delete_dashboard_stat(
    stat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Удалить статистику дашборда"""
    service = StatsService(db)
    deleted = await service.delete_dashboard_stat(stat_id)
    if not deleted:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Dashboard statistic not found")
    return {"message": "Dashboard statistic deleted successfully"}


@router.post("/refresh")
async def refresh_cached_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Обновить кэшированную статистику"""
    service = StatsService(db)
    await service.update_cached_stats()
    return {"message": "Cached statistics updated successfully"}
