"""
Visits Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from .models import Visit, Diagnosis, Treatment, VitalSigns, VisitStatus


class VisitsRepository:
    """Repository для работы с визитами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_visit_by_id(self, visit_id: int) -> Optional[Visit]:
        """Получить визит по ID"""
        result = await self.db.execute(select(Visit).filter(Visit.id == visit_id))
        return result.scalar_one_or_none()

    async def get_visits(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                   doctor_id: Optional[int] = None, status: Optional[VisitStatus] = None) -> List[Visit]:
        """Получить список визитов с фильтрами"""
        query = select(Visit)

        if patient_id:
            query = query.filter(Visit.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Visit.doctor_id == doctor_id)
        if status:
            query = query.filter(Visit.status == status)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_upcoming_visits(self, doctor_id: Optional[int] = None, limit: int = 50) -> List[Visit]:
        """Получить предстоящие визиты"""
        query = select(Visit).filter(
            Visit.visit_date >= datetime.utcnow(),
            Visit.status.in_([VisitStatus.SCHEDULED, VisitStatus.IN_PROGRESS])
        )

        if doctor_id:
            query = query.filter(Visit.doctor_id == doctor_id)

        result = await self.db.execute(query.order_by(Visit.visit_date).limit(limit))
        return result.scalars().all()

    async def create_visit(self, visit: Visit) -> Visit:
        """Создать новый визит"""
        self.db.add(visit)
        await self.db.commit()
        await self.db.refresh(visit)
        return visit

    async def update_visit(self, visit: Visit) -> Visit:
        """Обновить визит"""
        await self.db.commit()
        await self.db.refresh(visit)
        return visit

    async def delete_visit(self, visit: Visit) -> None:
        """Удалить визит"""
        await self.db.delete(visit)
        await self.db.commit()

    # Методы для работы с диагнозами
    async def add_diagnosis(self, diagnosis: Diagnosis) -> Diagnosis:
        """Добавить диагноз к визиту"""
        self.db.add(diagnosis)
        await self.db.commit()
        await self.db.refresh(diagnosis)
        return diagnosis

    async def get_diagnoses_by_visit(self, visit_id: int) -> List[Diagnosis]:
        """Получить диагнозы визита"""
        result = await self.db.execute(select(Diagnosis).filter(Diagnosis.visit_id == visit_id))
        return result.scalars().all()

    # Методы для работы с лечением
    async def add_treatment(self, treatment: Treatment) -> Treatment:
        """Добавить назначение лечения"""
        self.db.add(treatment)
        await self.db.commit()
        await self.db.refresh(treatment)
        return treatment

    async def get_treatments_by_visit(self, visit_id: int) -> List[Treatment]:
        """Получить назначения лечения визита"""
        result = await self.db.execute(select(Treatment).filter(Treatment.visit_id == visit_id))
        return result.scalars().all()

    # Методы для работы с жизненными показателями
    async def add_vital_signs(self, vital_signs: VitalSigns) -> VitalSigns:
        """Добавить жизненные показатели"""
        self.db.add(vital_signs)
        await self.db.commit()
        await self.db.refresh(vital_signs)
        return vital_signs

    async def get_vital_signs_by_visit(self, visit_id: int) -> Optional[VitalSigns]:
        """Получить жизненные показатели визита"""
        result = await self.db.execute(select(VitalSigns).filter(VitalSigns.visit_id == visit_id))
        return result.scalar_one_or_none()
