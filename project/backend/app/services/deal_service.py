from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.deal import Deal
from models.client import Client
from models.user import User
from dtos.deal import DealCreate, DealUpdate, DealStatus
from typing import List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DealService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, deal_data: DealCreate, created_by: int) -> Deal:
        client = await self.db.get(Client, deal_data.client_id)
        if not client:
            raise ValueError(f'Клиент с ID {deal_data.client_id} не найден')

        if deal_data.assigned_to:
            user = await self.db.get(User, deal_data.assigned_to)
            if not user:
                raise ValueError(f'Пользователь с ID {deal_data.assigned_to} не найден')

        deal = Deal(
            title=deal_data.title,
            client_id=deal_data.client_id,
            amount=deal_data.amount,
            status=deal_data.status.value,
            assigned_to=deal_data.assigned_to,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(deal)
        await self.db.commit()
        await self.db.refresh(deal)

        logger.info(f'Создана сделка {deal.id}: {deal.title}')
        return deal

    async def get_by_id(self, deal_id: int) -> Optional[Deal]:
        result = await self.db.execute(
            select(Deal).where(Deal.id == deal_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[DealStatus] = None,
            client_id: Optional[int] = None,
            assigned_to: Optional[int] = None
    ) -> Tuple[List[Deal], int]:

        query = select(Deal)
        count_query = select(func.count(Deal.id))

        if status:
            query = query.where(Deal.status == status.value)
            count_query = count_query.where(Deal.status == status.value)

        if client_id:
            query = query.where(Deal.client_id == client_id)
            count_query = count_query.where(Deal.client_id == client_id)

        if assigned_to:
            query = query.where(Deal.assigned_to == assigned_to)
            count_query = count_query.where(Deal.assigned_to == assigned_to)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.offset(skip).limit(limit).order_by(Deal.created_at.desc())
        result = await self.db.execute(query)
        deals = list(result.scalars().all())

        return deals, total

    async def update(
            self,
            deal_id: int,
            deal_data: DealUpdate,
            user_id: int
    ) -> Optional[Deal]:

        deal = await self.get_by_id(deal_id)
        if not deal:
            return None

        update_data = deal_data.model_dump(exclude_unset=True)

        if 'client_id' in update_data and update_data['client_id'] != deal.client_id:
            client = await self.db.get(Client, update_data['client_id'])
            if not client:
                raise ValueError(f'Клиент с ID {update_data["client_id"]} не найден')

        if 'assigned_to' in update_data and update_data['assigned_to'] != deal.assigned_to:
            if update_data['assigned_to']:
                user = await self.db.get(User, update_data['assigned_to'])
                if not user:
                    raise ValueError(f'Пользователь с ID {update_data["assigned_to"]} не найден')

        if 'status' in update_data:
            new_status = update_data['status']

            if new_status in [DealStatus.WON, DealStatus.LOST] and deal.closed_at is None:
                deal.closed_at = datetime.now()
                logger.info(f'Сделка {deal_id} закрыта со статусом {new_status.value}')

            elif new_status not in [DealStatus.WON, DealStatus.LOST] and deal.closed_at is not None:
                deal.closed_at = None
                logger.info(f'Сделка {deal_id} возвращена в работу')

            deal.status = new_status.value
            del update_data['status']

        for field, value in update_data.items():
            if hasattr(deal, field):
                setattr(deal, field, value)

        deal.updated_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(deal)

        logger.info(f'Сделка {deal_id} обновлена пользователем {user_id}')
        return deal

    async def delete(self, deal_id: int) -> bool:
        deal = await self.get_by_id(deal_id)
        if not deal:
            return False

        await self.db.delete(deal)
        await self.db.commit()
        logger.info(f'Сделка {deal_id} удалена')
        return True

    async def get_stats(self) -> dict:
        total_result = await self.db.execute(select(func.count(Deal.id)))
        total = total_result.scalar() or 0

        stats = {}
        for status in DealStatus:
            result = await self.db.execute(
                select(func.count(Deal.id)).where(Deal.status == status.value)
            )
            stats[status.value] = result.scalar() or 0

        won_result = await self.db.execute(
            select(func.sum(Deal.amount)).where(Deal.status == DealStatus.WON.value)
        )
        won_amount = float(won_result.scalar() or 0)

        return {
            'total': total,
            'by_status': stats,
            'won_amount': won_amount
        }