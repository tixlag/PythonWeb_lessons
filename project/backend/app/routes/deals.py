from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from database import get_db
from schemas.deal import DealCreate, DealUpdate, DealResponse, DealStats, DealStatus
from models.deal import Deal
from models.user import User
from deps.auth import get_current_user
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api/deals', tags=['Deals'])


@router.get('/', response_model=List[DealResponse])
async def get_deals(
    status: Optional[DealStatus] = Query(None, description='Фильтр по статусу'),
    client_id: Optional[int] = Query(None, description='Фильтр по клиенту'),
    assigned_to: Optional[int] = Query(None, description='Фильтр по ответственному'),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    
):
    logger.info(f'Запрос списка сделок от пользователя {current_user.id}')
    query = select(Deal)
    
    filters = []
    if status:
        filters.append(Deal.status == status.value)
    if client_id:
        filters.append(Deal.client_id == client_id)
    if assigned_to:
        filters.append(Deal.assigned_to == assigned_to)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    deals = result.scalars().all()
    
    return deals


@router.post('/', response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f'Создание новой сделки пользователем {current_user.id}')
    from app.models.client import Client
    client = await db.get(Client, deal_data.client_id)
    if not client:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f'Клиент с ID {deal_data.client_id} не найден'
        )
        
    if deal_data.assigned_to:
        user = await db.get(User, deal_data.assigned_to)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с ID {deal_data.assigned_to} не найден'
            )
    
    deal = Deal(
        title = deal_data.title,
        client_id = deal_data.client_id,
        amount = deal_data.amount,
        status = deal_data.status.value,
        assigned_to = deal_data.assigned_to,
        created_by = current_user.id,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )
    
    db.add(deal)
    await db.commit()
    await db. refresh(deal)
    
    logger.info(f'Сделка создана: ID={deal.id}')
    return deal

@router.get('/stats', response_model=DealStats)
async def get_deal_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f'Запрос статистики от пользователя {current_user.id}')
    
    total_result = await db.execute(select(func.count(Deal.id)))
    total = total_result.scalar() or 0
    
    stats = {}
    for status in DealStatus:
        result = await db.execute(
            select(func.count(Deal.id)).where(Deal.status == status.value)
        )
        stats[status.value] = result.scalar() or 0
        
    won_result = await db.execute(
        select(func.sum(Deal.amount)).where(Deal.status == DealStatus.WON.value)
    )
    won_amount = float(won_result.scalar() or 0)
    
    average_result = await db.execute(
        select(func.avg(Deal.amount)).where(Deal.status == DealStatus.WON.value)
    )
    average_check = float(average_result.scalar() or 0)
    
    return DealStats(
        total=total,
        by_status=stats,
        won_amount=won_amount,
        average_check=average_check
    )


@router.get('/{deal_id}', response_model=DealResponse)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f'Запрос сделки {deal_id} от пользователя {current_user.id}')
    
    deal = await db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Сделка не найдена'
        )
    
    return deal


@router.put('/{deal.id}', response_model=DealResponse)
async def update_deal(
    deal_id: int,
    
):
    pass




@router.delete('/{deal.id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    
):
    pass