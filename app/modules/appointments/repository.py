"""
Appointments Repository (Data Access Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .models import Appointment, AppointmentStatus


class AppointmentsRepository:
    """Repository для работы с записями на прием"""

    def __init__(self, db: Session):
        self.db = db

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Получить запись по ID"""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        status: Optional[AppointmentStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Appointment]:
        """Получить список записей с фильтрами"""
        query = self.db.query(Appointment)

        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        if status:
            query = query.filter(Appointment.status == status)
        if date_from:
            query = query.filter(Appointment.scheduled_date >= date_from)
        if date_to:
            query = query.filter(Appointment.scheduled_date <= date_to)

        return query.offset(skip).limit(limit).all()

    def get_upcoming_appointments(self, doctor_id: Optional[int] = None, limit: int = 50) -> List[Appointment]:
        """Получить предстоящие записи"""
        query = self.db.query(Appointment).filter(
            Appointment.scheduled_date >= datetime.now(),
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        )

        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        return query.order_by(Appointment.scheduled_date).limit(limit).all()

    def create_appointment(self, appointment: Appointment) -> Appointment:
        """Создать новую запись"""
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def update_appointment(self, appointment: Appointment) -> Appointment:
        """Обновить запись"""
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def delete_appointment(self, appointment: Appointment) -> None:
        """Удалить запись"""
        self.db.delete(appointment)
        self.db.commit()

    def check_availability(self, doctor_id: int, scheduled_date: datetime, duration_minutes: int) -> bool:
        """Проверить доступность времени для записи"""
        from sqlalchemy import and_, or_

        end_time = scheduled_date  # Время окончания приема

        # Находим пересекающиеся записи
        overlapping = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS]),
            or_(
                and_(Appointment.scheduled_date <= scheduled_date,
                     Appointment.scheduled_date >= end_time),
                and_(Appointment.scheduled_date >= scheduled_date,
                     Appointment.scheduled_date <= end_time)
            )
        ).first()

        return overlapping is None
