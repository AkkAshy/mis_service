"""
Patients Repository (Data Access Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Patient


class PatientsRepository:
    """Repository для работы с пациентами"""

    def __init__(self, db: Session):
        self.db = db

    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Получить пациента по ID"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def get_patients(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Patient]:
        """Получить список пациентов с пагинацией и поиском"""
        query = self.db.query(Patient)

        if search:
            # Поиск по имени, фамилии или телефону
            search_filter = f"%{search}%"
            query = query.filter(
                (Patient.first_name.ilike(search_filter)) |
                (Patient.last_name.ilike(search_filter)) |
                (Patient.phone.ilike(search_filter))
            )

        return query.offset(skip).limit(limit).all()

    def get_active_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Получить список активных пациентов"""
        return self.db.query(Patient).filter(Patient.is_active == "Y").offset(skip).limit(limit).all()

    def create_patient(self, patient: Patient) -> Patient:
        """Создать нового пациента"""
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def update_patient(self, patient: Patient) -> Patient:
        """Обновить пациента"""
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete_patient(self, patient: Patient) -> None:
        """Удалить пациента (мягкое удаление)"""
        patient.is_active = "N"
        self.db.commit()

    def search_patients_by_name(self, name: str, limit: int = 10) -> List[Patient]:
        """Поиск пациентов по имени"""
        search_filter = f"%{name}%"
        return self.db.query(Patient).filter(
            (Patient.first_name.ilike(search_filter)) |
            (Patient.last_name.ilike(search_filter))
        ).limit(limit).all()
