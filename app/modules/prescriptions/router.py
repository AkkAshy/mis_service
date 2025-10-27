"""
Prescriptions Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from .service import PrescriptionsService
from .schemas import Prescription, PrescriptionCreate, PrescriptionUpdate, PrescriptionSummary, Medication, MedicationBase
from .models import PrescriptionStatus

router = APIRouter()


@router.post("/", response_model=Prescription)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать новый рецепт"""
    service = PrescriptionsService(db)
    return await service.create_prescription(prescription_data, current_user.id)


@router.get("/", response_model=List[PrescriptionSummary])
async def get_prescriptions(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[PrescriptionStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить список рецептов с фильтрами"""
    service = PrescriptionsService(db)
    prescriptions = await service.get_prescriptions(skip, limit, patient_id, doctor_id, status)

    # Формируем краткую информацию
    result = []
    for prescription in prescriptions:
        result.append(PrescriptionSummary(
            id=prescription.id,
            patient_id=prescription.patient_id,
            patient_name=prescription.patient.full_name if prescription.patient else "Unknown",
            doctor_id=prescription.doctor_id,
            doctor_name=f"{prescription.doctor.full_name}" if prescription.doctor else "Unknown",
            status=prescription.status,
            prescription_date=prescription.prescription_date,
            medications_count=len(prescription.medications)
        ))

    return result


@router.get("/active", response_model=List[PrescriptionSummary])
async def get_active_prescriptions(
    patient_id: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить активные рецепты"""
    service = PrescriptionsService(db)
    prescriptions = await service.get_active_prescriptions(patient_id, limit)

    result = []
    for prescription in prescriptions:
        result.append(PrescriptionSummary(
            id=prescription.id,
            patient_id=prescription.patient_id,
            patient_name=prescription.patient.full_name if prescription.patient else "Unknown",
            doctor_id=prescription.doctor_id,
            doctor_name=f"{prescription.doctor.full_name}" if prescription.doctor else "Unknown",
            status=prescription.status,
            prescription_date=prescription.prescription_date,
            medications_count=len(prescription.medications)
        ))

    return result


@router.get("/{prescription_id}", response_model=Prescription)
async def get_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить рецепт по ID"""
    service = PrescriptionsService(db)
    prescription = await service.get_prescription(prescription_id)

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Проверяем права доступа (врач может видеть только свои рецепты, админ - все)
    if current_user.role not in ["admin"] and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return prescription


@router.put("/{prescription_id}", response_model=Prescription)
async def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить рецепт"""
    service = PrescriptionsService(db)
    prescription = await service.get_prescription(prescription_id)

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return await service.update_prescription(prescription_id, prescription_data)


@router.put("/{prescription_id}/complete", response_model=Prescription)
async def complete_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Завершить рецепт"""
    service = PrescriptionsService(db)
    prescription = await service.get_prescription(prescription_id)

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return await service.complete_prescription(prescription_id)


@router.delete("/{prescription_id}")
async def delete_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """Удалить рецепт (только для админов)"""
    service = PrescriptionsService(db)
    await service.delete_prescription(prescription_id)
    return {"message": "Prescription deleted successfully"}


# Эндпоинты для работы с лекарствами
@router.post("/{prescription_id}/medications", response_model=Medication)
async def add_medication(
    prescription_id: int,
    medication_data: MedicationBase,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Добавить лекарство к рецепту"""
    service = PrescriptionsService(db)
    prescription = await service.get_prescription(prescription_id)

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return await service.add_medication(prescription_id, medication_data)


@router.get("/{prescription_id}/medications", response_model=List[Medication])
async def get_prescription_medications(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить лекарства рецепта"""
    service = PrescriptionsService(db)
    prescription = await service.get_prescription(prescription_id)

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and prescription.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return await service.repository.get_medications_by_prescription(prescription_id)


@router.put("/medications/{medication_id}", response_model=Medication)
async def update_medication(
    medication_id: int,
    medication_data: MedicationBase,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить лекарство"""
    service = PrescriptionsService(db)
    return await service.update_medication(medication_id, medication_data)


@router.delete("/medications/{medication_id}")
async def delete_medication(
    medication_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить лекарство"""
    service = PrescriptionsService(db)
    await service.delete_medication(medication_id)
    return {"message": "Medication deleted successfully"}
