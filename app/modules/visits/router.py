"""
Visits Router (API Endpoints)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from .service import VisitsService

router = APIRouter()


# TODO: Реализовать эндпоинты
# Пример:
# @router.get("/")
# def get_all(
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     service = VisitsService(db)
#     return service.get_all()
