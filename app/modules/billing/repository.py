"""
Billing Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from .models import Billing


class BillingRepository:
    """Repository для работы с billing"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Billing]:
        """Получить все счета"""
        query = select(Billing)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, billing_id: int) -> Optional[Billing]:
        """Получить счет по ID"""
        query = select(Billing).where(Billing.id == billing_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_patient_id(self, patient_id: int) -> List[Billing]:
        """Получить счета по ID пациента"""
        query = select(Billing).where(Billing.patient_id == patient_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, billing: Billing) -> Billing:
        """Создать новый счет"""
        self.db.add(billing)
        await self.db.commit()
        await self.db.refresh(billing)
        return billing

    async def update(self, billing_id: int, update_data: dict) -> Optional[Billing]:
        """Обновить счет"""
        query = (
            update(Billing)
            .where(Billing.id == billing_id)
            .values(**update_data)
            .returning(Billing)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, billing_id: int) -> bool:
        """Удалить счет"""
        query = delete(Billing).where(Billing.id == billing_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
