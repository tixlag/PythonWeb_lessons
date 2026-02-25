from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dtos.auth import UserCreateDTO, UserLoginDTO, UserResponseDTO, TokenDTO
from services.auth_service import AuthService
from deps.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateDTO,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    service = AuthService(db)
    try:
        user = await service.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenDTO)
async def login(
    credentials: UserLoginDTO,
    db: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    service = AuthService(db)
    try:
        token_data = await service.login(credentials)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserResponseDTO)
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить данные текущего пользователя"""
    return current_user
