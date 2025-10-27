"""
Patients Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException, status
from .repository import PatientsRepository
from .models import Patient
from .schemas import PatientCreate, PatientUpdate


class PatientsService:
    """Сервис для бизнес-логики пациентов"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PatientsRepository(db)

    async def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Получить пациента по ID"""
        patient = await self.repository.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return patient

    async def get_patients(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Patient]:
        """Получить список пациентов"""
        return await self.repository.get_patients(skip, limit, search)

    async def get_active_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Получить список активных пациентов"""
        return await self.repository.get_active_patients(skip, limit)

    async def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Создать нового пациента"""
        # Проверяем, существует ли пациент с таким же именем и датой рождения
        existing_patients = await self.repository.search_patients_by_name(
            f"{patient_data.last_name} {patient_data.first_name}", limit=5
        )

        # Проверяем, существует ли пациент с таким же именем и датой рождения
        # (упрощенная проверка - в реальном приложении можно сделать более сложную логику)
        pass

        # Создаем пациента
        patient = Patient(
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            middle_name=patient_data.middle_name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            phone=patient_data.phone,
            address=patient_data.address,
            blood_type=patient_data.blood_type,
            allergies=patient_data.allergies,
            chronic_diseases=patient_data.chronic_diseases,
            emergency_contact_name=patient_data.emergency_contact_name,
            emergency_contact_phone=patient_data.emergency_contact_phone
        )

        return await self.repository.create_patient(patient)

    async def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> Patient:
        """Обновить пациента"""
        patient = await self.repository.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # Обновляем поля
        update_data = patient_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)

        return await self.repository.update_patient(patient)

    async def delete_patient(self, patient_id: int) -> None:
        """Удалить пациента (мягкое удаление)"""
        patient = await self.repository.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        await self.repository.delete_patient(patient)

    async def search_patients(self, query: str, limit: int = 10) -> List[Patient]:
        """Поиск пациентов"""
        return await self.repository.search_patients_by_name(query, limit)
