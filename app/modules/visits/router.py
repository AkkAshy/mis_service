"""
Visits Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from .service import VisitsService
from .schemas import Visit, VisitCreate, VisitUpdate, VisitSummary, Diagnosis, Treatment, VitalSigns, DiagnosisBase, TreatmentBase, VitalSignsBase
from .models import VisitStatus

router = APIRouter()


@router.post("/", response_model=Visit)
def create_visit(
    visit_data: VisitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать новый визит"""
    service = VisitsService(db)
    return service.create_visit(visit_data, current_user.id)


@router.get("/", response_model=List[VisitSummary])
def get_visits(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[VisitStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить список визитов с фильтрами"""
    service = VisitsService(db)
    visits = service.get_visits(skip, limit, patient_id, doctor_id, status)

    # Формируем краткую информацию
    result = []
    for visit in visits:
        result.append(VisitSummary(
            id=visit.id,
            patient_id=visit.patient_id,
            patient_name=visit.patient.full_name if visit.patient else "Unknown",
            doctor_id=visit.doctor_id,
            doctor_name=f"{visit.doctor.full_name}" if visit.doctor else "Unknown",
            status=visit.status,
            visit_date=visit.visit_date,
            chief_complaint=visit.chief_complaint
        ))

    return result


@router.get("/upcoming", response_model=List[VisitSummary])
def get_upcoming_visits(
    doctor_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить предстоящие визиты"""
    service = VisitsService(db)
    visits = service.get_upcoming_visits(doctor_id, limit)

    result = []
    for visit in visits:
        result.append(VisitSummary(
            id=visit.id,
            patient_id=visit.patient_id,
            patient_name=visit.patient.full_name if visit.patient else "Unknown",
            doctor_id=visit.doctor_id,
            doctor_name=f"{visit.doctor.full_name}" if visit.doctor else "Unknown",
            status=visit.status,
            visit_date=visit.visit_date,
            chief_complaint=visit.chief_complaint
        ))

    return result


@router.get("/{visit_id}", response_model=Visit)
def get_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить визит по ID"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа (врач может видеть только свои визиты, админ - все)
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return visit


@router.put("/{visit_id}", response_model=Visit)
def update_visit(
    visit_id: int,
    visit_data: VisitUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить визит"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.update_visit(visit_id, visit_data)


@router.put("/{visit_id}/complete", response_model=Visit)
def complete_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Завершить визит"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.complete_visit(visit_id)


@router.delete("/{visit_id}")
def delete_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """Удалить визит (только для админов)"""
    service = VisitsService(db)
    service.delete_visit(visit_id)
    return {"message": "Visit deleted successfully"}


# Эндпоинты для работы с диагнозами
@router.post("/{visit_id}/diagnoses", response_model=Diagnosis)
def add_diagnosis(
    visit_id: int,
    diagnosis_data: DiagnosisBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Добавить диагноз к визиту"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.add_diagnosis(visit_id, diagnosis_data)


@router.get("/{visit_id}/diagnoses", response_model=List[Diagnosis])
def get_visit_diagnoses(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить диагнозы визита"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.repository.get_diagnoses_by_visit(visit_id)


# Эндпоинты для работы с лечением
@router.post("/{visit_id}/treatments", response_model=Treatment)
def add_treatment(
    visit_id: int,
    treatment_data: TreatmentBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Добавить назначение лечения"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.add_treatment(visit_id, treatment_data)


@router.get("/{visit_id}/treatments", response_model=List[Treatment])
def get_visit_treatments(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить назначения лечения визита"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.repository.get_treatments_by_visit(visit_id)


# Эндпоинты для работы с жизненными показателями
@router.put("/{visit_id}/vital-signs", response_model=VitalSigns)
def update_vital_signs(
    visit_id: int,
    vital_signs_data: VitalSignsBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить жизненные показатели визита"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.update_vital_signs(visit_id, vital_signs_data)


@router.get("/{visit_id}/vital-signs", response_model=Optional[VitalSigns])
def get_visit_vital_signs(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить жизненные показатели визита"""
    service = VisitsService(db)
    visit = service.get_visit(visit_id)

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Проверяем права доступа
    if current_user.role not in ["admin"] and visit.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return service.repository.get_vital_signs_by_visit(visit_id)
