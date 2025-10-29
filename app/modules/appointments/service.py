"""
Appointments Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from .repository import AppointmentsRepository
from .models import Appointment, AppointmentStatus, AppointmentType
from .schemas import AppointmentCreate, AppointmentUpdate
from app.modules.visits.service import VisitsService
from app.modules.visits.schemas import VisitCreate


class AppointmentsService:
    """Сервис для бизнес-логики записей на прием"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AppointmentsRepository(db)

    async def get_appointment(self, appointment_id: int) -> Optional[Appointment]:
        """Получить запись по ID"""
        appointment = await self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        return appointment

    async def get_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        status_filter: Optional[AppointmentStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Appointment]:
        """Получить список записей с фильтрами"""
        return await self.repository.get_appointments(
            skip, limit, patient_id, doctor_id, status_filter, date_from, date_to
        )

    async def get_upcoming_appointments(self, doctor_id: Optional[int] = None, limit: int = 50) -> List[Appointment]:
        """Получить предстоящие записи"""
        return await self.repository.get_upcoming_appointments(doctor_id, limit)

    async def create_appointment(self, appointment_data: AppointmentCreate, created_by: int) -> Appointment:
        """Создать новую запись"""
        # Проверяем доступность времени
        if not await self.repository.check_availability(
            appointment_data.doctor_id,
            appointment_data.scheduled_date,
            appointment_data.duration_minutes
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time slot is not available"
            )

        # Проверяем, что дата в будущем
        if appointment_data.scheduled_date <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment date must be in the future"
            )

        # Создаем запись
        appointment = Appointment(
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_type=appointment_data.appointment_type,
            scheduled_date=appointment_data.scheduled_date,
            duration_minutes=appointment_data.duration_minutes,
            reason=appointment_data.reason,
            notes=appointment_data.notes,
            symptoms=appointment_data.symptoms,
            created_by=created_by
        )

        return await self.repository.create_appointment(appointment)

    async def update_appointment(self, appointment_id: int, appointment_data: AppointmentUpdate) -> Appointment:
        """Обновить запись"""
        appointment = await self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        # Если меняем время, проверяем доступность
        if appointment_data.scheduled_date and appointment_data.scheduled_date != appointment.scheduled_date:
            duration = appointment_data.duration_minutes or appointment.duration_minutes
            if not await self.repository.check_availability(
                appointment.doctor_id,
                appointment_data.scheduled_date,
                duration
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New time slot is not available"
                )

        # Обновляем поля
        update_data = appointment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)

        return await self.repository.update_appointment(appointment)

    async def cancel_appointment(self, appointment_id: int) -> Appointment:
        """Отменить запись"""
        appointment = await self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel completed or already cancelled appointment"
            )

        appointment.status = AppointmentStatus.CANCELLED
        return await self.repository.update_appointment(appointment)

    async def confirm_appointment(self, appointment_id: int) -> Appointment:
        """Подтвердить запись"""
        appointment = await self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        if appointment.status != AppointmentStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only scheduled appointments can be confirmed"
            )

        appointment.status = AppointmentStatus.CONFIRMED
        return await self.repository.update_appointment(appointment)

    async def complete_appointment(self, appointment_id: int, created_by: int) -> Appointment:
        """Завершить запись и создать визит"""
        appointment = await self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        if appointment.status not in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only confirmed or in-progress appointments can be completed"
            )

        appointment.status = AppointmentStatus.COMPLETED
        appointment = await self.repository.update_appointment(appointment)

        # Создаем визит на основе завершенной записи
        visit_service = VisitsService(self.db)
        visit_data = VisitCreate(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            visit_date=datetime.now(),  # Используем текущее время как дату визита
            chief_complaint=appointment.symptoms,  # Симптомы как основная жалоба
            history_of_present_illness=None,
            physical_examination=None,
            assessment=None,
            plan=None
        )
        visit = await visit_service.create_visit(visit_data, created_by)

        # Добавляем ID визита к ответу
        appointment.visit_id = visit.id

        return appointment
