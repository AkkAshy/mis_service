"""
Stats Service (Business Logic Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import StatsRepository


class StatsService:
    """Сервис для бизнес-логики stats"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = StatsRepository(db)

    # TODO: Реализовать бизнес-логику
    pass
