"""
Prescriptions Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .models import Prescription, Medication, PrescriptionStatus


class PrescriptionsRepository:
    """Repository для работы с рецептами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_prescription_by_id(self, prescription_id: int) -> Optional[Prescription]:
        """Получить рецепт по ID"""
        result = await self.db.execute(select(Prescription).filter(Prescription.id == prescription_id))
        return result.scalar_one_or_none()

    async def get_prescriptions(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                         doctor_id: Optional[int] = None, status: Optional[PrescriptionStatus] = None) -> List[Prescription]:
        """Получить список рецептов с фильтрами"""
        query = select(Prescription)

        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Prescription.doctor_id == doctor_id)
        if status:
            query = query.filter(Prescription.status == status)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_active_prescriptions(self, patient_id: Optional[int] = None, limit: int = 50) -> List[Prescription]:
        """Получить активные рецепты"""
        query = select(Prescription).filter(Prescription.status == PrescriptionStatus.ACTIVE)

        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)

        result = await self.db.execute(query.order_by(Prescription.prescription_date.desc()).limit(limit))
        return result.scalars().all()

    async def create_prescription(self, prescription: Prescription) -> Prescription:
        """Создать новый рецепт"""
        self.db.add(prescription)
        await self.db.commit()
        await self.db.refresh(prescription)
        return prescription

    async def update_prescription(self, prescription: Prescription) -> Prescription:
        """Обновить рецепт"""
        await self.db.commit()
        await self.db.refresh(prescription)
        return prescription

    async def delete_prescription(self, prescription: Prescription) -> None:
        """Удалить рецепт"""
        await self.db.delete(prescription)
        await self.db.commit()

    # Методы для работы с лекарствами
    async def add_medication(self, medication: Medication) -> Medication:
        """Добавить лекарство к рецепту"""
        self.db.add(medication)
        await self.db.commit()
        await self.db.refresh(medication)
        return medication

    async def get_medications_by_prescription(self, prescription_id: int) -> List[Medication]:
        """Получить лекарства рецепта"""
        result = await self.db.execute(select(Medication).filter(Medication.prescription_id == prescription_id))
        return result.scalars().all()

    async def update_medication(self, medication: Medication) -> Medication:
        """Обновить лекарство"""
        await self.db.commit()
        await self.db.refresh(medication)
        return medication

    async def delete_medication(self, medication: Medication) -> None:
        """Удалить лекарство"""
        await self.db.delete(medication)
        await self.db.commit()
