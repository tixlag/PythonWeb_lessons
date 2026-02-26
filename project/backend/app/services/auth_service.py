from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from dtos.auth import UserCreateDTO
from utils.auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from config import settings
from typing import Optional


class AuthService:
    """Сервис для работы с аутентификацией"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreateDTO) -> User:
        """Регистрация нового пользователя"""
        # Проверка, что пользователь уже существует
        result = await self.db.execute(
            select(User).where(
                (User.username == user_data.username) |
                (User.email == user_data.email)
            )
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Пользователь уже существует")

        # Создание нового пользователя
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, credentials: OAuth2PasswordRequestForm) -> dict:
        """Вход в систему"""
        result = await self.db.execute(
            select(User).where(User.username == credentials.username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Неверные учетные данные")

        if not user.is_active:
            raise ValueError("Пользователь неактивен")

        # Создание токена
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
