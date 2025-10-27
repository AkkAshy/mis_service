"""
Patients Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .models import Patient


class PatientsRepository:
    """Repository для работы с пациентами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Получить пациента по ID"""
        result = await self.db.execute(select(Patient).filter(Patient.id == patient_id))
        return result.scalar_one_or_none()

    async def get_patients(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Patient]:
        """Получить список пациентов с пагинацией и поиском"""
        query = select(Patient)

        if search:
            # Поиск по имени, фамилии или телефону
            search_filter = f"%{search}%"
            query = query.filter(
                (Patient.first_name.ilike(search_filter)) |
                (Patient.last_name.ilike(search_filter)) |
                (Patient.phone.ilike(search_filter))
            )

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_active_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Получить список активных пациентов"""
        result = await self.db.execute(select(Patient).filter(Patient.is_active == "Y").offset(skip).limit(limit))
        return result.scalars().all()

    async def create_patient(self, patient: Patient) -> Patient:
        """Создать нового пациента"""
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def update_patient(self, patient: Patient) -> Patient:
        """Обновить пациента"""
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def delete_patient(self, patient: Patient) -> None:
        """Удалить пациента (мягкое удаление)"""
        patient.is_active = "N"
        await self.db.commit()

    async def search_patients_by_name(self, name: str, limit: int = 10) -> List[Patient]:
        """Поиск пациентов по имени"""
        search_filter = f"%{name}%"
        result = await self.db.execute(select(Patient).filter(
            (Patient.first_name.ilike(search_filter)) |
            (Patient.last_name.ilike(search_filter))
        ).limit(limit))
        return result.scalars().all()
