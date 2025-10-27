"""
Appointments Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from .service import AppointmentsService
from .schemas import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentSummary
from .models import AppointmentStatus

router = APIRouter()


@router.get("/", response_model=List[AppointmentSummary])
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    patient_id: Optional[int] = Query(None, ge=1),
    doctor_id: Optional[int] = Query(None, ge=1),
    status: Optional[AppointmentStatus] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить список записей с фильтрами"""
    service = AppointmentsService(db)
    return await service.get_appointments(skip, limit, patient_id, doctor_id, status, date_from, date_to)


@router.get("/upcoming", response_model=List[AppointmentSummary])
async def get_upcoming_appointments(
    doctor_id: Optional[int] = Query(None, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить предстоящие записи"""
    service = AppointmentsService(db)
    return await service.get_upcoming_appointments(doctor_id, limit)


@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(
    appointment_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить запись по ID"""
    service = AppointmentsService(db)
    return await service.get_appointment(appointment_id)


@router.post("/", response_model=Appointment)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Создать новую запись на прием"""
    service = AppointmentsService(db)
    return await service.create_appointment(appointment_data, current_user.id)


@router.put("/{appointment_id}", response_model=Appointment)
async def update_appointment(
    appointment_data: AppointmentUpdate,
    appointment_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Обновить запись на прием"""
    service = AppointmentsService(db)
    return await service.update_appointment(appointment_id, appointment_data)


@router.post("/{appointment_id}/confirm", response_model=Appointment)
async def confirm_appointment(
    appointment_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Подтвердить запись на прием"""
    service = AppointmentsService(db)
    return await service.confirm_appointment(appointment_id)


@router.post("/{appointment_id}/cancel", response_model=Appointment)
async def cancel_appointment(
    appointment_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отменить запись на прием"""
    service = AppointmentsService(db)
    return await service.cancel_appointment(appointment_id)


@router.post("/{appointment_id}/complete", response_model=Appointment)
async def complete_appointment(
    appointment_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Завершить запись на прием"""
    service = AppointmentsService(db)
    return await service.complete_appointment(appointment_id)
