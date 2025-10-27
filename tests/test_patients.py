"""
Unit tests for patients module
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from app.modules.patients.service import PatientsService
from app.modules.patients.schemas import PatientCreate, PatientUpdate


def test_create_patient(db: Session):
    """Test patient creation"""
    service = PatientsService(db)

    patient_data = PatientCreate(
        first_name="Иван",
        last_name="Иванов",
        middle_name="Иванович",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        phone="+7-999-999-99-99",
        address="г. Москва, ул. Ленина, д. 1",
        blood_type="A+",
        allergies="Нет",
        chronic_diseases="Нет",
        emergency_contact_name="Мария Иванова",
        emergency_contact_phone="+7-999-999-99-98"
    )

    patient = service.create_patient(patient_data)

    assert patient.first_name == "Иван"
    assert patient.last_name == "Иванов"
    assert patient.phone == "+7-999-999-99-99"
    assert patient.blood_type == "A+"


def test_get_patient(db: Session):
    """Test get patient by ID"""
    service = PatientsService(db)

    # Create patient first
    patient_data = PatientCreate(
        first_name="Иван",
        last_name="Иванов",
        middle_name="Иванович",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        phone="+7-999-999-99-99",
        address="г. Москва, ул. Ленина, д. 1",
        blood_type="A+",
        allergies="Нет",
        chronic_diseases="Нет",
        emergency_contact_name="Мария Иванова",
        emergency_contact_phone="+7-999-999-99-98"
    )
    created_patient = service.create_patient(patient_data)

    # Get patient
    patient = service.get_patient(created_patient.id)

    assert patient.id == created_patient.id
    assert patient.first_name == "Иван"


def test_update_patient(db: Session):
    """Test patient update"""
    service = PatientsService(db)

    # Create patient first
    patient_data = PatientCreate(
        first_name="Иван",
        last_name="Иванов",
        middle_name="Иванович",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        phone="+7-999-999-99-99",
        address="г. Москва, ул. Ленина, д. 1",
        blood_type="A+",
        allergies="Нет",
        chronic_diseases="Нет",
        emergency_contact_name="Мария Иванова",
        emergency_contact_phone="+7-999-999-99-98"
    )
    created_patient = service.create_patient(patient_data)

    # Update patient
    update_data = PatientUpdate(phone="+7-999-999-99-97")
    updated_patient = service.update_patient(created_patient.id, update_data)

    assert updated_patient.phone == "+7-999-999-99-97"


def test_create_patient_endpoint(client: TestClient):
    """Test create patient endpoint"""
    patient_data = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "phone": "+7-999-999-99-99",
        "address": "г. Москва, ул. Ленина, д. 1",
        "blood_type": "A+",
        "allergies": "Нет",
        "chronic_diseases": "Нет",
        "emergency_contact_name": "Мария Иванова",
        "emergency_contact_phone": "+7-999-999-99-98"
    }

    response = client.post("/patients/", json=patient_data)
    assert response.status_code == 201

    data = response.json()
    assert data["first_name"] == "Иван"
    assert data["last_name"] == "Иванов"


def test_get_patients_endpoint(client: TestClient):
    """Test get patients endpoint"""
    # Create a patient first
    patient_data = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "phone": "+7-999-999-99-99",
        "address": "г. Москва, ул. Ленина, д. 1",
        "blood_type": "A+",
        "allergies": "Нет",
        "chronic_diseases": "Нет",
        "emergency_contact_name": "Мария Иванова",
        "emergency_contact_phone": "+7-999-999-99-98"
    }
    client.post("/patients/", json=patient_data)

    # Get patients
    response = client.get("/patients/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert data[0]["first_name"] == "Иван"


def test_search_patients_endpoint(client: TestClient):
    """Test search patients endpoint"""
    # Create a patient first
    patient_data = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "phone": "+7-999-999-99-99",
        "address": "г. Москва, ул. Ленина, д. 1",
        "blood_type": "A+",
        "allergies": "Нет",
        "chronic_diseases": "Нет",
        "emergency_contact_name": "Мария Иванова",
        "emergency_contact_phone": "+7-999-999-99-98"
    }
    client.post("/patients/", json=patient_data)

    # Search patients
    response = client.get("/patients/search/?query=Иван")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert "Иван" in data[0]["first_name"] or "Иван" in data[0]["last_name"]