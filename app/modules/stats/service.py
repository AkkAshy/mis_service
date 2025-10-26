"""
Stats Service (Business Logic Layer)
"""
from sqlalchemy.orm import Session
from .repository import StatsRepository


class StatsService:
    """Сервис для бизнес-логики stats"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = StatsRepository(db)
    
    # TODO: Реализовать бизнес-логику
    pass
