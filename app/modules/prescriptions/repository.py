"""
Prescriptions Repository (Data Access Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Prescription, Medication, PrescriptionStatus


class PrescriptionsRepository:
    """Repository для работы с рецептами"""

    def __init__(self, db: Session):
        self.db = db

    def get_prescription_by_id(self, prescription_id: int) -> Optional[Prescription]:
        """Получить рецепт по ID"""
        return self.db.query(Prescription).filter(Prescription.id == prescription_id).first()

    def get_prescriptions(self, skip: int = 0, limit: int = 100, patient_id: Optional[int] = None,
                         doctor_id: Optional[int] = None, status: Optional[PrescriptionStatus] = None) -> List[Prescription]:
        """Получить список рецептов с фильтрами"""
        query = self.db.query(Prescription)

        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Prescription.doctor_id == doctor_id)
        if status:
            query = query.filter(Prescription.status == status)

        return query.offset(skip).limit(limit).all()

    def get_active_prescriptions(self, patient_id: Optional[int] = None, limit: int = 50) -> List[Prescription]:
        """Получить активные рецепты"""
        query = self.db.query(Prescription).filter(Prescription.status == PrescriptionStatus.ACTIVE)

        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)

        return query.order_by(Prescription.prescription_date.desc()).limit(limit).all()

    def create_prescription(self, prescription: Prescription) -> Prescription:
        """Создать новый рецепт"""
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def update_prescription(self, prescription: Prescription) -> Prescription:
        """Обновить рецепт"""
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def delete_prescription(self, prescription: Prescription) -> None:
        """Удалить рецепт"""
        self.db.delete(prescription)
        self.db.commit()

    # Методы для работы с лекарствами
    def add_medication(self, medication: Medication) -> Medication:
        """Добавить лекарство к рецепту"""
        self.db.add(medication)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def get_medications_by_prescription(self, prescription_id: int) -> List[Medication]:
        """Получить лекарства рецепта"""
        return self.db.query(Medication).filter(Medication.prescription_id == prescription_id).all()

    def update_medication(self, medication: Medication) -> Medication:
        """Обновить лекарство"""
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def delete_medication(self, medication: Medication) -> None:
        """Удалить лекарство"""
        self.db.delete(medication)
        self.db.commit()
