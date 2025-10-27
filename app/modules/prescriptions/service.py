"""
Prescriptions Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from fastapi import HTTPException, status
from .repository import PrescriptionsRepository
from .models import Prescription, Medication, PrescriptionStatus
from .schemas import PrescriptionCreate, PrescriptionUpdate, MedicationBase


class PrescriptionsService:
    """Сервис для бизнес-логики рецептов"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PrescriptionsRepository(db)

    async def get_prescription(self, prescription_id: int) -> Optional[Prescription]:
        """Получить рецепт по ID"""
        return await self.repository.get_prescription_by_id(prescription_id)

    async def get_prescriptions(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                         doctor_id: Optional[int] = None, status: Optional[PrescriptionStatus] = None) -> List[Prescription]:
        """Получить список рецептов с фильтрами"""
        return await self.repository.get_prescriptions(skip, limit, patient_id, doctor_id, status)

    async def get_active_prescriptions(self, patient_id: Optional[int] = None, limit: int = 50) -> List[Prescription]:
        """Получить активные рецепты"""
        return await self.repository.get_active_prescriptions(patient_id, limit)

    async def create_prescription(self, prescription_data: PrescriptionCreate, created_by: int) -> Prescription:
        """Создать новый рецепт"""
        # Проверяем, что пациент существует
        from app.modules.patients.models import Patient
        result = await self.db.execute(select(Patient).filter(Patient.id == prescription_data.patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Проверяем, что врач существует
        from app.modules.auth.models import User
        result = await self.db.execute(select(User).filter(User.id == prescription_data.doctor_id))
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Проверяем визит, если указан
        if prescription_data.visit_id:
            from app.modules.visits.models import Visit
            result = await self.db.execute(select(Visit).filter(Visit.id == prescription_data.visit_id))
            visit = result.scalar_one_or_none()
            if not visit:
                raise HTTPException(status_code=404, detail="Visit not found")

        # Создаем рецепт
        prescription = Prescription(
            patient_id=prescription_data.patient_id,
            doctor_id=prescription_data.doctor_id,
            visit_id=prescription_data.visit_id,
            notes=prescription_data.notes,
            follow_up_date=prescription_data.follow_up_date,
            created_by=created_by
        )

        prescription = await self.repository.create_prescription(prescription)

        # Добавляем лекарства
        for medication_data in prescription_data.medications:
            medication = Medication(
                prescription_id=prescription.id,
                **medication_data.dict()
            )
            await self.repository.add_medication(medication)

        return prescription

    async def update_prescription(self, prescription_id: int, prescription_data: PrescriptionUpdate) -> Prescription:
        """Обновить рецепт"""
        prescription = await self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        # Обновляем поля
        update_data = prescription_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prescription, field, value)

        return await self.repository.update_prescription(prescription)

    async def delete_prescription(self, prescription_id: int) -> None:
        """Удалить рецепт"""
        prescription = await self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        await self.repository.delete_prescription(prescription)

    async def complete_prescription(self, prescription_id: int) -> Prescription:
        """Завершить рецепт"""
        prescription = await self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        if prescription.status == PrescriptionStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Prescription is already completed")

        prescription.status = PrescriptionStatus.COMPLETED
        return await self.repository.update_prescription(prescription)

    async def add_medication(self, prescription_id: int, medication_data: MedicationBase) -> Medication:
        """Добавить лекарство к рецепту"""
        prescription = await self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")

        medication = Medication(
            prescription_id=prescription_id,
            **medication_data.dict()
        )
        return await self.repository.add_medication(medication)

    async def update_medication(self, medication_id: int, medication_data: MedicationBase) -> Medication:
        """Обновить лекарство"""
        result = await self.db.execute(select(Medication).filter(Medication.id == medication_id))
        medication = result.scalar_one_or_none()
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")

        update_data = medication_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(medication, field, value)

        return await self.repository.update_medication(medication)

    async def delete_medication(self, medication_id: int) -> None:
        """Удалить лекарство"""
        result = await self.db.execute(select(Medication).filter(Medication.id == medication_id))
        medication = result.scalar_one_or_none()
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")

        await self.repository.delete_medication(medication)
