"""
Stats Router (API Endpoints)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from .service import StatsService

router = APIRouter()


# TODO: Реализовать эндпоинты
# Пример:
# @router.get("/")
# async def get_all(
#     db: AsyncSession = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     service = StatsService(db)
#     return await service.get_all()
