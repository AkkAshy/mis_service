"""
Prescriptions Service (Business Logic Layer)
"""
from sqlalchemy.orm import Session
from .repository import PrescriptionsRepository


class PrescriptionsService:
    """Сервис для бизнес-логики prescriptions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PrescriptionsRepository(db)
    
    # TODO: Реализовать бизнес-логику
    pass
