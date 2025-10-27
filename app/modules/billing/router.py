"""
Billing Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from .service import BillingService
from .schemas import BillingCreate, BillingUpdate, Billing

router = APIRouter()


@router.get("/", response_model=List[Billing])
async def get_all_billing(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Получить все счета"""
    service = BillingService(db)
    return await service.get_all_billing()


@router.get("/{billing_id}", response_model=Billing)
async def get_billing(
    billing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Получить счет по ID"""
    service = BillingService(db)
    billing = await service.get_billing_by_id(billing_id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing


@router.get("/patient/{patient_id}", response_model=List[Billing])
async def get_billing_by_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Получить счета по ID пациента"""
    service = BillingService(db)
    return await service.get_billing_by_patient(patient_id)


@router.post("/", response_model=Billing)
async def create_billing(
    billing_data: BillingCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Создать новый счет"""
    service = BillingService(db)
    return await service.create_billing(billing_data, current_user.id)


@router.put("/{billing_id}", response_model=Billing)
async def update_billing(
    billing_id: int,
    billing_data: BillingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Обновить счет"""
    service = BillingService(db)
    billing = await service.update_billing(billing_id, billing_data)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing


@router.put("/{billing_id}/pay", response_model=Billing)
async def mark_billing_as_paid(
    billing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Отметить счет как оплаченный"""
    service = BillingService(db)
    billing = await service.mark_as_paid(billing_id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return billing


@router.delete("/{billing_id}")
async def delete_billing(
    billing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Удалить счет"""
    service = BillingService(db)
    deleted = await service.delete_billing(billing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return {"message": "Billing record deleted successfully"}
