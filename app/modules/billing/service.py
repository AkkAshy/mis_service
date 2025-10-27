"""
Billing Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from .repository import BillingRepository
from .models import Billing, BillingStatus
from .schemas import BillingCreate, BillingUpdate, Billing as BillingSchema


class BillingService:
    """Сервис для бизнес-логики billing"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BillingRepository(db)

    async def get_all_billing(self) -> List[BillingSchema]:
        """Получить все счета"""
        billing_records = await self.repository.get_all()
        return [BillingSchema.from_orm(record) for record in billing_records]

    async def get_billing_by_id(self, billing_id: int) -> Optional[BillingSchema]:
        """Получить счет по ID"""
        billing = await self.repository.get_by_id(billing_id)
        return BillingSchema.from_orm(billing) if billing else None

    async def get_billing_by_patient(self, patient_id: int) -> List[BillingSchema]:
        """Получить счета по ID пациента"""
        billing_records = await self.repository.get_by_patient_id(patient_id)
        return [BillingSchema.from_orm(record) for record in billing_records]

    async def create_billing(self, billing_data: BillingCreate, created_by: int) -> BillingSchema:
        """Создать новый счет"""
        billing = Billing(
            **billing_data.dict(),
            created_by=created_by
        )
        created_billing = await self.repository.create(billing)
        return BillingSchema.from_orm(created_billing)

    async def update_billing(self, billing_id: int, update_data: BillingUpdate) -> Optional[BillingSchema]:
        """Обновить счет"""
        update_dict = update_data.dict(exclude_unset=True)
        if update_data.status == BillingStatus.PAID.value and not update_data.payment_date:
            update_dict['payment_date'] = datetime.utcnow()

        updated_billing = await self.repository.update(billing_id, update_dict)
        return BillingSchema.from_orm(updated_billing) if updated_billing else None

    async def delete_billing(self, billing_id: int) -> bool:
        """Удалить счет"""
        return await self.repository.delete(billing_id)

    async def mark_as_paid(self, billing_id: int) -> Optional[BillingSchema]:
        """Отметить счет как оплаченный"""
        update_data = BillingUpdate(
            status=BillingStatus.PAID.value,
            payment_date=datetime.utcnow()
        )
        return await self.update_billing(billing_id, update_data)
