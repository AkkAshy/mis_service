"""
Prescriptions Repository (Data Access Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional


class PrescriptionsRepository:
    """Repository для работы с prescriptions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # TODO: Реализовать методы работы с БД
    pass
