"""
Operations Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from .service import OperationsService
from .schemas import Surgery, SurgeryCreate, SurgeryUpdate, SurgerySummary

router = APIRouter()


@router.get("/", response_model=List[SurgerySummary])
async def get_surgeries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    patient_id: Optional[int] = Query(None, ge=1),
    surgeon_id: Optional[int] = Query(None, ge=1),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список операций с фильтрами"""
    service = OperationsService(db)
    surgeries = await service.get_surgeries(skip, limit, patient_id, surgeon_id, start_date, end_date)
    return list(surgeries)


@router.get("/upcoming", response_model=List[SurgerySummary])
async def get_upcoming_surgeries(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить предстоящие операции"""
    service = OperationsService(db)
    surgeries = await service.get_upcoming_surgeries(limit)
    return list(surgeries)


@router.get("/recent", response_model=List[SurgerySummary])
async def get_recent_surgeries(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить недавние операции"""
    service = OperationsService(db)
    surgeries = await service.get_recent_surgeries(days, limit)
    return list(surgeries)


@router.get("/patient/{patient_id}", response_model=List[SurgerySummary])
async def get_patient_surgeries(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить операции пациента"""
    service = OperationsService(db)
    surgeries = await service.get_patient_surgeries(patient_id, skip, limit)
    return list(surgeries)


@router.get("/surgeon/{surgeon_id}", response_model=List[SurgerySummary])
async def get_surgeon_surgeries(
    surgeon_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить операции хирурга"""
    service = OperationsService(db)
    surgeries = await service.get_surgeon_surgeries(surgeon_id, skip, limit)
    return list(surgeries)


@router.get("/{surgery_id}", response_model=Surgery)
async def get_surgery(
    surgery_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить операцию по ID"""
    service = OperationsService(db)
    return await service.get_surgery(surgery_id)


@router.post("/", response_model=Surgery)
async def create_surgery(
    surgery_data: SurgeryCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin", "doctor"))
):
    """Создать новую операцию"""
    service = OperationsService(db)
    return await service.create_surgery(surgery_data, current_user.id)


@router.put("/{surgery_id}", response_model=Surgery)
async def update_surgery(
    surgery_id: int,
    surgery_data: SurgeryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin", "doctor"))
):
    """Обновить операцию"""
    service = OperationsService(db)
    return await service.update_surgery(surgery_id, surgery_data)


@router.delete("/{surgery_id}")
async def delete_surgery(
    surgery_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Удалить операцию"""
    service = OperationsService(db)
    await service.delete_surgery(surgery_id)
    return {"message": "Surgery deleted successfully"}