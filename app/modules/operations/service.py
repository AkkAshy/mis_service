"""
Operations Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Sequence
from datetime import datetime
from fastapi import HTTPException, status
from .repository import OperationsRepository
from .models import Surgery
from .schemas import SurgeryCreate, SurgeryUpdate
from app.modules.patients.repository import PatientsRepository


class OperationsService:
    """Сервис для бизнес-логики операций"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OperationsRepository(db)
        self.patients_repository = PatientsRepository(db)

    async def get_surgery(self, surgery_id: int) -> Optional[Surgery]:
        """Получить операцию по ID"""
        surgery = await self.repository.get_surgery_by_id(surgery_id)
        if not surgery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Surgery not found"
            )
        return surgery

    async def get_surgeries(
        self,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        surgeon_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Sequence[Surgery]:
        """Получить список операций с фильтрами"""
        return await self.repository.get_surgeries(skip, limit, patient_id, surgeon_id, start_date, end_date)

    async def get_patient_surgeries(self, patient_id: int, skip: int = 0, limit: int = 50) -> Sequence[Surgery]:
        """Получить операции пациента"""
        # Проверяем, существует ли пациент
        patient = await self.patients_repository.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        return await self.repository.get_surgeries_by_patient(patient_id, skip, limit)

    async def get_surgeon_surgeries(self, surgeon_id: int, skip: int = 0, limit: int = 50) -> Sequence[Surgery]:
        """Получить операции хирурга"""
        return await self.repository.get_surgeries_by_surgeon(surgeon_id, skip, limit)

    async def create_surgery(self, surgery_data: SurgeryCreate, created_by: int) -> Surgery:
        """Создать новую операцию"""
        # Проверяем, существует ли пациент
        patient = await self.patients_repository.get_patient_by_id(surgery_data.patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # Проверяем, что время окончания не раньше времени начала
        if surgery_data.end_time and surgery_data.end_time <= surgery_data.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )

        # Создаем операцию
        surgery = Surgery(
            patient_id=surgery_data.patient_id,
            surgeon_id=surgery_data.surgeon_id,
            operation_name=surgery_data.operation_name,
            operation_date=surgery_data.operation_date,
            start_time=surgery_data.start_time,
            end_time=surgery_data.end_time,
            pre_op_days=surgery_data.pre_op_days,
            post_op_days=surgery_data.post_op_days,
            notes=surgery_data.notes,
            complications=surgery_data.complications,
            outcome=surgery_data.outcome,
            additional_data=surgery_data.additional_data,
            created_by=created_by
        )

        return await self.repository.create_surgery(surgery)

    async def update_surgery(self, surgery_id: int, surgery_data: SurgeryUpdate) -> Surgery:
        """Обновить операцию"""
        surgery = await self.repository.get_surgery_by_id(surgery_id)
        if not surgery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Surgery not found"
            )

        # Проверяем временные ограничения при обновлении
        if surgery_data.end_time is not None:
            start_time = surgery_data.start_time if surgery_data.start_time is not None else surgery.start_time
            if isinstance(start_time, datetime) and surgery_data.end_time <= start_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End time must be after start time"
                )

        # Обновляем поля
        update_data = surgery_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(surgery, field, value)

        return await self.repository.update_surgery(surgery)

    async def delete_surgery(self, surgery_id: int) -> None:
        """Удалить операцию"""
        surgery = await self.repository.get_surgery_by_id(surgery_id)
        if not surgery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Surgery not found"
            )

        await self.repository.delete_surgery(surgery)

    async def get_upcoming_surgeries(self, limit: int = 20) -> Sequence[Surgery]:
        """Получить предстоящие операции"""
        return await self.repository.get_upcoming_surgeries(limit)

    async def get_recent_surgeries(self, days: int = 30, limit: int = 50) -> Sequence[Surgery]:
        """Получить недавние операции"""
        return await self.repository.get_recent_surgeries(days, limit)