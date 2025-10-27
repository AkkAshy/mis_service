"""
Database indexes for frequently queried fields
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for frequently queried fields"""

    # Users table indexes
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'])

    # Patients table indexes
    op.create_index('ix_patients_first_name', 'patients', ['first_name'])
    op.create_index('ix_patients_last_name', 'patients', ['last_name'])
    op.create_index('ix_patients_phone', 'patients', ['phone'])
    op.create_index('ix_patients_date_of_birth', 'patients', ['date_of_birth'])
    op.create_index('ix_patients_is_active', 'patients', ['is_active'])

    # Composite index for patient search (name + active status)
    op.create_index('ix_patients_name_active', 'patients', ['last_name', 'first_name', 'is_active'])

    # Appointments table indexes
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('ix_appointments_doctor_id', 'appointments', ['doctor_id'])
    op.create_index('ix_appointments_status', 'appointments', ['status'])
    op.create_index('ix_appointments_scheduled_date', 'appointments', ['scheduled_date'])
    op.create_index('ix_appointments_created_by', 'appointments', ['created_by'])

    # Composite indexes for appointments
    op.create_index('ix_appointments_doctor_date', 'appointments', ['doctor_id', 'scheduled_date'])
    op.create_index('ix_appointments_patient_date', 'appointments', ['patient_id', 'scheduled_date'])
    op.create_index('ix_appointments_status_date', 'appointments', ['status', 'scheduled_date'])

    # Prescriptions table indexes (if exists)
    try:
        op.create_index('ix_prescriptions_patient_id', 'prescriptions', ['patient_id'])
        op.create_index('ix_prescriptions_doctor_id', 'prescriptions', ['doctor_id'])
        op.create_index('ix_prescriptions_status', 'prescriptions', ['status'])
        op.create_index('ix_prescriptions_prescription_date', 'prescriptions', ['prescription_date'])
    except Exception:
        # Table might not exist yet
        pass

    # Visits table indexes (if exists)
    try:
        op.create_index('ix_visits_patient_id', 'visits', ['patient_id'])
        op.create_index('ix_visits_doctor_id', 'visits', ['doctor_id'])
        op.create_index('ix_visits_visit_date', 'visits', ['visit_date'])
        op.create_index('ix_visits_status', 'visits', ['status'])
    except Exception:
        # Table might not exist yet
        pass


def downgrade():
    """Remove indexes"""

    # Remove users indexes
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_role', table_name='users')

    # Remove patients indexes
    op.drop_index('ix_patients_first_name', table_name='patients')
    op.drop_index('ix_patients_last_name', table_name='patients')
    op.drop_index('ix_patients_phone', table_name='patients')
    op.drop_index('ix_patients_date_of_birth', table_name='patients')
    op.drop_index('ix_patients_is_active', table_name='patients')
    op.drop_index('ix_patients_name_active', table_name='patients')

    # Remove appointments indexes
    op.drop_index('ix_appointments_patient_id', table_name='appointments')
    op.drop_index('ix_appointments_doctor_id', table_name='appointments')
    op.drop_index('ix_appointments_status', table_name='appointments')
    op.drop_index('ix_appointments_scheduled_date', table_name='appointments')
    op.drop_index('ix_appointments_created_by', table_name='appointments')
    op.drop_index('ix_appointments_doctor_date', table_name='appointments')
    op.drop_index('ix_appointments_patient_date', table_name='appointments')
    op.drop_index('ix_appointments_status_date', table_name='appointments')

    # Remove prescriptions indexes (if exist)
    try:
        op.drop_index('ix_prescriptions_patient_id', table_name='prescriptions')
        op.drop_index('ix_prescriptions_doctor_id', table_name='prescriptions')
        op.drop_index('ix_prescriptions_status', table_name='prescriptions')
        op.drop_index('ix_prescriptions_prescription_date', table_name='prescriptions')
    except Exception:
        pass

    # Remove visits indexes (if exist)
    try:
        op.drop_index('ix_visits_patient_id', table_name='visits')
        op.drop_index('ix_visits_doctor_id', table_name='visits')
        op.drop_index('ix_visits_visit_date', table_name='visits')
        op.drop_index('ix_visits_status', table_name='visits')
    except Exception:
        pass