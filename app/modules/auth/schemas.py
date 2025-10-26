"""
Auth Schemas (Pydantic)
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from .models import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email адрес")
    full_name: str = Field(..., min_length=2, max_length=100, description="Полное имя")
    role: UserRole = Field(default=UserRole.DOCTOR, description="Роль пользователя")


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100, description="Пароль")


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """Полная схема пользователя"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для входа в систему"""
    username: str = Field(..., description="Имя пользователя или email")
    password: str = Field(..., description="Пароль")


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные токена"""
    username: Optional[str] = None
