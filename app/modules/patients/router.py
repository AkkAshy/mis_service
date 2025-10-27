"""
Patients Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from .service import PatientsService
from .schemas import Patient, PatientCreate, PatientUpdate, PatientSummary

router = APIRouter()


@router.get("/", response_model=List[PatientSummary])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список пациентов с поиском и пагинацией"""
    service = PatientsService(db)
    return await service.get_patients(skip, limit, search)


@router.get("/active", response_model=List[PatientSummary])
async def get_active_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список активных пациентов"""
    service = PatientsService(db)
    return await service.get_active_patients(skip, limit)


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить пациента по ID"""
    service = PatientsService(db)
    return await service.get_patient(patient_id)


@router.post("/", response_model=Patient)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать нового пациента"""
    service = PatientsService(db)
    return await service.create_patient(patient_data)


@router.put("/{patient_id}", response_model=Patient)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновить данные пациента"""
    service = PatientsService(db)
    return await service.update_patient(patient_id, patient_data)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin", "doctor"))
):
    """Удалить пациента (мягкое удаление)"""
    service = PatientsService(db)
    await service.delete_patient(patient_id)
    return {"message": "Patient deleted successfully"}


@router.get("/search/", response_model=List[PatientSummary])
async def search_patients(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Поиск пациентов по имени"""
    service = PatientsService(db)
    return await service.search_patients(query, limit)
