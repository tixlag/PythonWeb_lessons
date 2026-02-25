from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreateDTO(BaseModel):
    """DTO для регистрации нового пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=3)
    full_name: str | None = None


class UserLoginDTO(BaseModel):
    """DTO для входа в систему"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)


class UserResponseDTO(BaseModel):
    """DTO для ответа с данными пользователя"""
    id: int
    username: str
    email: str
    full_name: str | None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenDTO(BaseModel):
    """DTO для ответа с токеном"""
    access_token: str
    token_type: str = "bearer"
