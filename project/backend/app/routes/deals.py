from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dtos.deal import DealCreate, DealUpdate, DealResponse, DealStats, DealStatus
from services.deal_service import DealService
from models.user import User
from deps.auth import get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api/deals', tags=['Deals'])


@router.get('/', response_model=List[DealResponse])
async def get_deals(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        status: Optional[DealStatus] = Query(None),
        client_id: Optional[int] = Query(None),
        assigned_to: Optional[int] = Query(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    logger.info(f'Запрос списка сделок от пользователя {current_user.id}')

    service = DealService(db)
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
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    logger.info(f'Создание новой сделки пользователем {current_user.id}')

    service = DealService(db)

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
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f'Запрос статистики от пользователя {current_user.id}')

    service = DealService(db)
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
        current_user: User = Depends(get_current_user)
):
    logger.info(f'Запрос сделки {deal_id} от пользователя {current_user.id}')

    service = DealService(db)
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
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f'Обновление сделки {deal_id} пользователем {current_user.id}')

    service = DealService(db)

    try:
        deal = await service.update(deal_id, deal_data, user_id=current_user.id)

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Сделка не найдена'
            )

<<<<<<< HEAD
    if deal_data.assigned_to:
        user = await db.get(User, deal_data.assigned_to)  # убрали запятую
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с ID {deal_data.assigned_to} не найден'
            )

    update_data = deal_data.model_dump(exclude_unset=True, mode='python') # больше узнать о методе и про разные mode

    if 'status' in update_data:
        new_status = update_data['status'].value

        if new_status in ['won', 'lost'] and deal.closed_at is None:
            deal.closed_at = datetime.now
            logger.info(f'Сделка {deal_id} закрыта со статусом {new_status}')

        elif new_status not in ['won', 'lost'] and deal.closed_at:
            deal.closed_at = None
            logger.info(f'Сделка {deal_id} возвращена в работу')

        deal.status = new_status
        del update_data['status']

    for field, value in update_data.items():
        if hasattr(deal, field):
            setattr(deal, field, value)

    deal.updated_at = datetime.now()  # добавили ()

    await db.commit()
    await db.refresh(deal)

    logger.info(f'Сделка {deal_id} обновлена')
    return deal
=======
        logger.info(f'Сделка {deal_id} обновлена')
        return deal

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
>>>>>>> 276d4c0 (feat: Добавление deal_service)


@router.delete('/{deal_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
        deal_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    logger.info(f'Удаление сделки {deal_id} пользователем {current_user.id}')

    service = DealService(db)
    success = await service.delete(deal_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Сделка не найдена'
        )

    logger.info(f'Сделка {deal_id} удалена')
    return None