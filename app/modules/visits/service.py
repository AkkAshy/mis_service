"""
Visits Service (Business Logic Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime
from .repository import VisitsRepository
from .models import Visit, Diagnosis, Treatment, VitalSigns, VisitStatus
from .schemas import VisitCreate, VisitUpdate, DiagnosisBase, TreatmentBase, VitalSignsBase


class VisitsService:
    """Сервис для бизнес-логики визитов"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = VisitsRepository(db)

    def get_visit(self, visit_id: int) -> Optional[Visit]:
        """Получить визит по ID"""
        return self.repository.get_visit_by_id(visit_id)

    def get_visits(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                   doctor_id: Optional[int] = None, status: Optional[VisitStatus] = None) -> List[Visit]:
        """Получить список визитов с фильтрами"""
        return self.repository.get_visits(skip, limit, patient_id, doctor_id, status)

    def get_upcoming_visits(self, doctor_id: Optional[int] = None, limit: int = 50) -> List[Visit]:
        """Получить предстоящие визиты"""
        return self.repository.get_upcoming_visits(doctor_id, limit)

    def create_visit(self, visit_data: VisitCreate, created_by: int) -> Visit:
        """Создать новый визит"""
        # Проверяем, что пациент существует
        from app.modules.patients.models import Patient
        patient = self.db.query(Patient).filter(Patient.id == visit_data.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Проверяем, что врач существует
        from app.modules.auth.models import User
        doctor = self.db.query(User).filter(User.id == visit_data.doctor_id).first()
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

        visit = self.repository.create_visit(visit)

        # Добавляем связанные данные
        if visit_data.vital_signs:
            vital_signs = VitalSigns(
                visit_id=visit.id,
                **visit_data.vital_signs.dict(exclude_unset=True)
            )
            self.repository.add_vital_signs(vital_signs)

        for diagnosis_data in visit_data.diagnoses or []:
            diagnosis = Diagnosis(
                visit_id=visit.id,
                **diagnosis_data.dict()
            )
            self.repository.add_diagnosis(diagnosis)

        for treatment_data in visit_data.treatments or []:
            treatment = Treatment(
                visit_id=visit.id,
                **treatment_data.dict()
            )
            self.repository.add_treatment(treatment)

        return visit

    def update_visit(self, visit_id: int, visit_data: VisitUpdate) -> Visit:
        """Обновить визит"""
        visit = self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Обновляем поля
        update_data = visit_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(visit, field, value)

        return self.repository.update_visit(visit)

    def delete_visit(self, visit_id: int) -> None:
        """Удалить визит"""
        visit = self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        self.repository.delete_visit(visit)

    def complete_visit(self, visit_id: int) -> Visit:
        """Завершить визит"""
        visit = self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        if visit.status == VisitStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Visit is already completed")

        visit.status = VisitStatus.COMPLETED
        return self.repository.update_visit(visit)

    def add_diagnosis(self, visit_id: int, diagnosis_data: DiagnosisBase) -> Diagnosis:
        """Добавить диагноз к визиту"""
        visit = self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        diagnosis = Diagnosis(
            visit_id=visit_id,
            **diagnosis_data.dict()
        )
        return self.repository.add_diagnosis(diagnosis)

    def add_treatment(self, visit_id: int, treatment_data: TreatmentBase) -> Treatment:
        """Добавить назначение лечения"""
        visit = self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        treatment = Treatment(
            visit_id=visit_id,
            **treatment_data.dict()
        )
        return self.repository.add_treatment(treatment)

    def update_vital_signs(self, visit_id: int, vital_signs_data: VitalSignsBase) -> VitalSigns:
        """Обновить жизненные показатели"""
        visit = self.repository.get_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Удаляем старые показатели, если есть
        existing = self.repository.get_vital_signs_by_visit(visit_id)
        if existing:
            self.db.delete(existing)
            self.db.commit()

        # Создаем новые
        vital_signs = VitalSigns(
            visit_id=visit_id,
            **vital_signs_data.dict(exclude_unset=True)
        )
        return self.repository.add_vital_signs(vital_signs)
