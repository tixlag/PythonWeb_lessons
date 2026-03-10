from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dtos.deal import DealCreate, DealUpdate, DealResponse, DealStats, DealStatus
from services.deal_service import DealService
from models.user import User
from deps.auth import get_current_user
from typing import List, Optional, Annotated
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api/deals', tags=['Deals'])

DealServiceDep = Annotated[DealService, Depends(DealService)]

@router.get('/', response_model=List[DealResponse])
async def get_deals(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        status: Optional[DealStatus] = Query(None),
        client_id: Optional[int] = Query(None),
        assigned_to: Optional[int] = Query(None),
        current_user: User = Depends(get_current_user),
        service: DealServiceDep = None,
):
    logger.info(f'Запрос списка сделок от пользователя {current_user.id}')

    deals, total = await service.get_all(
        skip=skip,
        limit=limit,
        status=status,
        client_id=client_id,
        assigned_to=assigned_to
    )

    return deals


@router.post('/', response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
        deal_data: DealCreate,
        current_user=Depends(get_current_user),
    service = DealServiceDep,
):
    logger.info(f'Создание новой сделки пользователем {current_user.id}')

    try:
        deal = await service.create(deal_data, created_by=current_user.id)
        logger.info(f'Сделка создана: ID={deal.id}')
        return deal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get('/stats', response_model=DealStats)
async def get_deal_stats(
        current_user: User = Depends(get_current_user),
        service: DealServiceDep = None,
):
    logger.info(f'Запрос статистики от пользователя {current_user.id}')

    stats = await service.get_stats()

    return DealStats(
        total=stats['total'],
        by_status=stats['by_status'],
        won_amount=stats['won_amount'],
        average_check=0
    )


@router.get('/{deal_id}', response_model=DealResponse)
async def get_deal(
        deal_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        service: DealServiceDep = None
):
    logger.info(f'Запрос сделки {deal_id} от пользователя {current_user.id}')

    deal = await service.get_by_id(deal_id)

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Сделка не найдена'
        )

    return deal


@router.put('/{deal_id}', response_model=DealResponse)
async def update_deal(
        deal_id: int,
        deal_data: DealUpdate,
        current_user: User = Depends(get_current_user),
        service: DealServiceDep = None
):
    logger.info(f'Обновление сделки {deal_id} пользователем {current_user.id}')


    try:
        deal = await service.update(deal_id, deal_data, user_id=current_user.id)

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Сделка не найдена'
            )

        logger.info(f'Сделка {deal_id} обновлена')
        return deal

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete('/{deal_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
        deal_id: int,
        current_user: User = Depends(get_current_user),
        service: DealServiceDep = None
):
    logger.info(f'Удаление сделки {deal_id} пользователем {current_user.id}')

    success = await service.delete(deal_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Сделка не найдена'
        )

    logger.info(f'Сделка {deal_id} удалена')
    return None