"""
Operations Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Sequence
from datetime import datetime
from .models import Surgery


class OperationsRepository:
    """Repository для работы с операциями"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_surgery_by_id(self, surgery_id: int) -> Optional[Surgery]:
        """Получить операцию по ID"""
        result = await self.db.execute(
            select(Surgery).filter(Surgery.id == surgery_id)
        )
        return result.scalar_one_or_none()

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
        query = select(Surgery)

        # Применяем фильтры
        if patient_id:
            query = query.filter(Surgery.patient_id == patient_id)

        if surgeon_id:
            query = query.filter(Surgery.surgeon_id == surgeon_id)

        if start_date:
            query = query.filter(Surgery.operation_date >= start_date)

        if end_date:
            query = query.filter(Surgery.operation_date <= end_date)

        # Сортировка по дате операции (новые сначала)
        query = query.order_by(Surgery.operation_date.desc())

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_surgeries_by_patient(self, patient_id: int, skip: int = 0, limit: int = 50) -> Sequence[Surgery]:
        """Получить операции пациента"""
        result = await self.db.execute(
            select(Surgery)
            .filter(Surgery.patient_id == patient_id)
            .order_by(Surgery.operation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_surgeries_by_surgeon(self, surgeon_id: int, skip: int = 0, limit: int = 50) -> Sequence[Surgery]:
        """Получить операции хирурга"""
        result = await self.db.execute(
            select(Surgery)
            .filter(Surgery.surgeon_id == surgeon_id)
            .order_by(Surgery.operation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_surgery(self, surgery: Surgery) -> Surgery:
        """Создать новую операцию"""
        self.db.add(surgery)
        await self.db.commit()
        await self.db.refresh(surgery)
        return surgery

    async def update_surgery(self, surgery: Surgery) -> Surgery:
        """Обновить операцию"""
        await self.db.commit()
        await self.db.refresh(surgery)
        return surgery

    async def delete_surgery(self, surgery: Surgery) -> None:
        """Удалить операцию"""
        await self.db.delete(surgery)
        await self.db.commit()

    async def get_upcoming_surgeries(self, limit: int = 20) -> Sequence[Surgery]:
        """Получить предстоящие операции"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Surgery)
            .filter(Surgery.operation_date >= now)
            .order_by(Surgery.operation_date.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_surgeries(self, days: int = 30, limit: int = 50) -> Sequence[Surgery]:
        """Получить недавние операции за указанное количество дней"""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(Surgery)
            .filter(Surgery.operation_date >= start_date)
            .order_by(Surgery.operation_date.desc())
            .limit(limit)
        )
        return result.scalars().all()