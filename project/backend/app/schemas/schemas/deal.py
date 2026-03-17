from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import DealStatus

class DealCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description='Название сделки')
    client_id: int = Field(..., gt=0, description='ID клиента')
    amount: float = Field(..., ge=0, description='Сумма сделки')
    status: DealStatus = Field(default=DealStatus.NEW, description='Статус сделки')
    assigned_to: Optional[int] = Field(None, gt=0, description='ID ответственного пользователя')
    
class DealUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description='Название сделки')
    client_id: Optional[int] = Field(None, gt=0, description='ID клиента')
    amount: Optional[float] = Field(None, ge=0, description='Сумма сделки')
    status: Optional[DealStatus] = Field(None, description='Статус сделки')
    assigned_to: Optional[int] = Field(None, gt=0, description='ID ответственного пользователя')
    
class DealResponse(BaseModel):
    id: int
    created_by: int
    amount: float
    status: DealStatus
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        
class DealStats(BaseModel):
    total: int
    by_status: dict[str, int]
    won_amount: float
    avg_check: float