"""
Auth Repository (Data Access Layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .models import User


class AuthRepository:
    """Repository для работы с пользователями"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей с пагинацией"""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_user(self, user: User) -> User:
        """Создать нового пользователя"""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user: User) -> User:
        """Обновить пользователя"""
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        """Удалить пользователя"""
        await self.db.delete(user)
        await self.db.commit()

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентифицировать пользователя"""
        from app.core.security import verify_password

        user = await self.get_user_by_username(username)
        if not user:
            user = await self.get_user_by_email(username)

        if user and verify_password(password, user.hashed_password):
            return user
        return None
