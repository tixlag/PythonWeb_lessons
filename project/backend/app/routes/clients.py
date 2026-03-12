from sqlalchemy import select

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dtos.client import ClientResponse
from models import Client
from models.user import User
from deps.auth import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api/clients', tags=['Clients'])

@router.get('/', response_model=List[ClientResponse])
async def get_clients(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db) ,
):
    logger.info(f'Запрос списка клиентов от пользователя {current_user.id}')
    query = select(Client)
    result = await db.execute(query)
    clients = list(result.scalars().all())
    return clients
