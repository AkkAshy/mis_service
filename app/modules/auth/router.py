"""
Auth Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.security import create_access_token
from app.core.config import settings
from .service import AuthService
from .schemas import User, UserCreate, UserUpdate, Token, UserLogin

router = APIRouter()


@router.post("/register", response_model=User)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    service = AuthService(db)
    return service.create_user(user_data)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Вход в систему"""
    service = AuthService(db)
    user = service.authenticate_user(UserLogin(username=form_data.username, password=form_data.password))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/users", response_model=List[User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Получить список пользователей (только для админов)"""
    service = AuthService(db)
    return service.get_users(skip, limit)


@router.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить пользователя по ID"""
    service = AuthService(db)
    user = service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Пользователи могут видеть только свою информацию, админы - всех
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return user


@router.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить пользователя"""
    # Пользователи могут обновлять только свою информацию, админы - всех
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = AuthService(db)
    return service.update_user(user_id, user_data)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Удалить пользователя (только для админов)"""
    service = AuthService(db)
    service.delete_user(user_id)
    return {"message": "User deleted successfully"}
