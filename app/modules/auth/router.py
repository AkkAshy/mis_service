"""
Auth Router (API Endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import timedelta

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings
from .service import AuthService
from .schemas import User, UserCreate, UserUpdate, Token, UserLogin

router = APIRouter()


@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    print(f"🔐 Регистрация пользователя: {user_data.username}")
    try:
        service = AuthService(db)
        user = await service.create_user(user_data)

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        refresh_token = create_access_token(
            data={"sub": user.username}, expires_delta=refresh_token_expires
        )

        print(f"✅ Пользователь зарегистрирован: {user.username} (role: {user.role}, full_name: {user.full_name})")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "refresh_token": refresh_token
        }
    except Exception as e:
        print(f"❌ Ошибка регистрации: {e}")
        raise


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    print(f"🔐 Попытка входа: {form_data.username}")
    try:
        service = AuthService(db)
        user = await service.authenticate_user(UserLogin(username=form_data.username, password=form_data.password))

        if not user:
            print(f"❌ Неверные учетные данные для: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        refresh_token = create_access_token(
            data={"sub": user.username}, expires_delta=refresh_token_expires
        )

        print(f"✅ Успешный вход: {user.username} (role: {user.role}, full_name: {user.full_name})")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "refresh_token": refresh_token
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка входа: {e}")
        raise


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.get("/users", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Получить список пользователей (только для админов)"""
    service = AuthService(db)
    return await service.get_users(skip, limit)


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить пользователя по ID"""
    service = AuthService(db)
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Пользователи могут видеть только свою информацию, админы - всех
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return user


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить пользователя"""
    # Пользователи могут обновлять только свою информацию, админы - всех
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = AuthService(db)
    return await service.update_user(user_id, user_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Обновление access токена с помощью refresh токена"""
    try:
        payload = decode_access_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        service = AuthService(db)
        user = await service.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        new_refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        new_refresh_token = create_access_token(
            data={"sub": user.username}, expires_delta=new_refresh_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "refresh_token": new_refresh_token
        }
    except Exception as e:
        print(f"❌ Ошибка обновления токена: {e}")
        raise


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Удалить пользователя (только для админов)"""
    service = AuthService(db)
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}
