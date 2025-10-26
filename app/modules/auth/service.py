"""
Auth Service (Business Logic Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from .repository import AuthRepository
from .models import User
from .schemas import UserCreate, UserUpdate, UserLogin


class AuthService:
    """Сервис для бизнес-логики аутентификации"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthRepository(db)

    def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.repository.get_user_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени"""
        return self.repository.get_user_by_username(username)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей"""
        return self.repository.get_users(skip, limit)

    def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        # Проверяем, существует ли пользователь
        if self.repository.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        if self.repository.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Создаем пользователя
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role
        )

        return self.repository.create_user(user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновить пользователя"""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Обновляем поля
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        return self.repository.update_user(user)

    def delete_user(self, user_id: int) -> None:
        """Удалить пользователя"""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        self.repository.delete_user(user)

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Аутентифицировать пользователя"""
        return self.repository.authenticate_user(login_data.username, login_data.password)
