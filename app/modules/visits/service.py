"""
Visits Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime
from .repository import VisitsRepository
from .models import Visit, Diagnosis, Treatment, VitalSigns, VisitStatus
from .schemas import VisitCreate, VisitUpdate, DiagnosisBase, TreatmentBase, VitalSignsBase


class VisitsService:
    """Сервис для бизнес-логики визитов"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = VisitsRepository(db)

    async def get_visit(self, visit_id: int) -> Optional[Visit]:
        """Получить визит по ID"""
        return await self.repository.get_visit_by_id(visit_id)

    async def get_visits(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                   doctor_id: Optional[int] = None, status: Optional[VisitStatus] = None) -> List[Visit]:
        """Получить список визитов с фильтрами"""
        return await self.repository.get_visits(skip, limit, patient_id, doctor_id, status)

    async def get_upcoming_visits(self, doctor_id: Optional[int] = None, limit: int = 50) -> List[Visit]:
        """Получить предстоящие визиты"""
        return await self.repository.get_upcoming_visits(doctor_id, limit)

    async def create_visit(self, visit_data: VisitCreate, created_by: int) -> Visit:
        """Создать новый визит"""
        # Проверяем, что пациент существует
        from app.modules.patients.models import Patient
        result = await self.db.execute(select(Patient).filter(Patient.id == visit_data.patient_id))
        patient = result.scalar_one_or_none()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Проверяем, что врач существует
        from app.modules.auth.models import User
        result = await self.db.execute(select(User).filter(User.id == visit_data.doctor_id))
        doctor = result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Создаем визит
        visit = Visit(
            patient_id=visit_data.patient_id,
            doctor_id=visit_data.doctor_id,
            appointment_id=visit_data.appointment_id,
            visit_date=visit_data.visit_date,
            chief_complaint=visit_data.chief_complaint,
            history_of_present_illness=visit_data.history_of_present_illness,
            physical_examination=visit_data.physical_examination,
            assessment=visit_data.assessment,
            plan=visit_data.plan,
            created_by=created_by
        )

        visit = await self.repository.create_visit(visit)

        # Добавляем связанные данные
        if visit_data.vital_signs:
            vital_signs = VitalSigns(
                visit_id=visit.id,
                **visit_data.vital_signs.dict(exclude_unset=True)
            )
            await self.repository.add_vital_signs(vital_signs)

        for diagnosis_data in visit_data.diagnoses or []:
            diagnosis = Diagnosis(
                visit_id=visit.id,
                **diagnosis_data.dict()
            )
            await self.repository.add_diagnosis(diagnosis)

        for treatment_data in visit_data.treatments or []:
            treatment = Treatment(
                visit_id=visit.id,
                **treatment_data.dict()
            )
            await self.repository.add_treatment(treatment)

        return visit

    async def update_visit(self, visit_id: int, visit_data: VisitUpdate) -> Visit:
        """Обновить визит"""
        visit = await self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Обновляем поля
        update_data = visit_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(visit, field, value)

        return await self.repository.update_visit(visit)

    async def delete_visit(self, visit_id: int) -> None:
        """Удалить визит"""
        visit = await self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        await self.repository.delete_visit(visit)

    async def complete_visit(self, visit_id: int) -> Visit:
        """Завершить визит"""
        visit = await self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        if visit.status == VisitStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Visit is already completed")

        visit.status = VisitStatus.COMPLETED
        return await self.repository.update_visit(visit)

    async def add_diagnosis(self, visit_id: int, diagnosis_data: DiagnosisBase) -> Diagnosis:
        """Добавить диагноз к визиту"""
        visit = await self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        diagnosis = Diagnosis(
            visit_id=visit_id,
            **diagnosis_data.dict()
        )
        return await self.repository.add_diagnosis(diagnosis)

    async def add_treatment(self, visit_id: int, treatment_data: TreatmentBase) -> Treatment:
        """Добавить назначение лечения"""
        visit = await self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        treatment = Treatment(
            visit_id=visit_id,
            **treatment_data.dict()
        )
        return await self.repository.add_treatment(treatment)

    async def update_vital_signs(self, visit_id: int, vital_signs_data: VitalSignsBase) -> VitalSigns:
        """Обновить жизненные показатели"""
        visit = await self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Удаляем старые показатели, если есть
        existing = await self.repository.get_vital_signs_by_visit(visit_id)
        if existing:
            await self.db.delete(existing)
            await self.db.commit()

        # Создаем новые
        vital_signs = VitalSigns(
            visit_id=visit_id,
            **vital_signs_data.dict(exclude_unset=True)
        )
        return await self.repository.add_vital_signs(vital_signs)
