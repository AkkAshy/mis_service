"""
Stats Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional


class StatsRepository:
    """Repository для работы с stats"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # TODO: Реализовать методы работы с БД
    pass
