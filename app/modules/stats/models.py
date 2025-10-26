"""
Stats Models
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


# TODO: Определить модели для модуля stats
# Пример:
# class Stats(Base):
#     __tablename__ = "stats"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
