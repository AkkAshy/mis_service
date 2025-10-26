"""
Auth Repository (Data Access Layer)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import User


class AuthRepository:
    """Repository для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей с пагинацией"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user: User) -> User:
        """Создать нового пользователя"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: User) -> User:
        """Обновить пользователя"""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        """Удалить пользователя"""
        self.db.delete(user)
        self.db.commit()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентифицировать пользователя"""
        from app.core.security import verify_password

        user = self.get_user_by_username(username)
        if not user:
            user = self.get_user_by_email(username)

        if user and verify_password(password, user.hashed_password):
            return user
        return None
