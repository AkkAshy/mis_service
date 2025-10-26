"""
Visits Repository (Data Access Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .models import Visit, Diagnosis, Treatment, VitalSigns, VisitStatus


class VisitsRepository:
    """Repository для работы с визитами"""

    def __init__(self, db: Session):
        self.db = db

    def get_visit_by_id(self, visit_id: int) -> Optional[Visit]:
        """Получить визит по ID"""
        return self.db.query(Visit).filter(Visit.id == visit_id).first()

    def get_visits(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                   doctor_id: Optional[int] = None, status: Optional[VisitStatus] = None) -> List[Visit]:
        """Получить список визитов с фильтрами"""
        query = self.db.query(Visit)

        if patient_id:
            query = query.filter(Visit.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Visit.doctor_id == doctor_id)
        if status:
            query = query.filter(Visit.status == status)

        return query.offset(skip).limit(limit).all()

    def get_upcoming_visits(self, doctor_id: Optional[int] = None, limit: int = 50) -> List[Visit]:
        """Получить предстоящие визиты"""
        query = self.db.query(Visit).filter(
            Visit.visit_date >= datetime.utcnow(),
            Visit.status.in_([VisitStatus.SCHEDULED, VisitStatus.IN_PROGRESS])
        )

        if doctor_id:
            query = query.filter(Visit.doctor_id == doctor_id)

        return query.order_by(Visit.visit_date).limit(limit).all()

    def create_visit(self, visit: Visit) -> Visit:
        """Создать новый визит"""
        self.db.add(visit)
        self.db.commit()
        self.db.refresh(visit)
        return visit

    def update_visit(self, visit: Visit) -> Visit:
        """Обновить визит"""
        self.db.commit()
        self.db.refresh(visit)
        return visit

    def delete_visit(self, visit: Visit) -> None:
        """Удалить визит"""
        self.db.delete(visit)
        self.db.commit()

    # Методы для работы с диагнозами
    def add_diagnosis(self, diagnosis: Diagnosis) -> Diagnosis:
        """Добавить диагноз к визиту"""
        self.db.add(diagnosis)
        self.db.commit()
        self.db.refresh(diagnosis)
        return diagnosis

    def get_diagnoses_by_visit(self, visit_id: int) -> List[Diagnosis]:
        """Получить диагнозы визита"""
        return self.db.query(Diagnosis).filter(Diagnosis.visit_id == visit_id).all()

    # Методы для работы с лечением
    def add_treatment(self, treatment: Treatment) -> Treatment:
        """Добавить назначение лечения"""
        self.db.add(treatment)
        self.db.commit()
        self.db.refresh(treatment)
        return treatment

    def get_treatments_by_visit(self, visit_id: int) -> List[Treatment]:
        """Получить назначения лечения визита"""
        return self.db.query(Treatment).filter(Treatment.visit_id == visit_id).all()

    # Методы для работы с жизненными показателями
    def add_vital_signs(self, vital_signs: VitalSigns) -> VitalSigns:
        """Добавить жизненные показатели"""
        self.db.add(vital_signs)
        self.db.commit()
        self.db.refresh(vital_signs)
        return vital_signs

    def get_vital_signs_by_visit(self, visit_id: int) -> Optional[VitalSigns]:
        """Получить жизненные показатели визита"""
        return self.db.query(VitalSigns).filter(VitalSigns.visit_id == visit_id).first()
