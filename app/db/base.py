"""
Импорт всех моделей для Alembic
Добавляй сюда импорты моделей по мере создания
"""
from app.db.session import Base

# Импорты моделей
from app.modules.auth.models import User
from app.modules.patients.models import Patient
from app.modules.appointments.models import Appointment
from app.modules.visits.models import Visit, Diagnosis, Treatment, VitalSigns
from app.modules.prescriptions.models import Prescription, Medication
from app.modules.operations.models import Surgery
from app.modules.stats.models import SystemStats, DashboardStats
from app.modules.billing.models import Billing
