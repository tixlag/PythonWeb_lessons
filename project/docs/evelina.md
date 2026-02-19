# Инструкция для Backend Developer — Эвелина

**Роль:** Backend Developer  
**Зона ответственности:** Сделки (Deals)  
**Стек:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic

---

## Общие обязанности

1. Реализация API для сущности "Сделка" (Deal)
2. Работа с базой данных
3. Валидация входных данных через DTO
4. Бизнес-логика в сервисах
5. Управление статусами сделок
6. Взаимодействие с Frontend (Александр)

---

## DDD Архитектура

### Структура файлов для сделок

```
app/
├── models/
│   └── deal.py          # SQLAlchemy модель
├── dtos/
│   └── deal.py         # Pydantic DTO
├── services/
│   └── deal_service.py # Бизнес-логика
└── routes/
    └── deals.py       # HTTP эндпоинты
```

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Настройка рабочего окружения
**Инструменты:** Git, Python, VS Code

**Задачи:**
1. Клонировать репозиторий
2. Создать ветку: `git checkout -b feature/deals-evelina`
3. Установить зависимости
4. Проверить, что проект запускается

**Ожидаемый результат:** Проект запускается локально

---

#### 1.2 Изучение структуры проекта
**Инструменты:** Изучение кода

**Изучить:**
- Модель Client (посмотреть у Сони)
- DTO клиента (посмотреть у Сони)
- Сервис клиента (посмотреть у Сони)
- Как работают роутеры (посмотреть у Даниила)
- Как настроена аутентификация

**Ожидаемый результат:** Понимание DDD архитектуры проекта

---

## Этап 2: Модель Deal (Неделя 7-8)

### Теоретический материал

### Статусы сделки в CRM

Стандартные статусы:
- **New** — Новая сделка
- **Negotiation** — Переговоры
- **Won** — Выиграна
- **Lost** — Проиграна

### Поля сделки

- Название
- Клиент (связь)
- Сумма
- Статус
- Ответственный (пользователь)
- Даты создания/обновления/закрытия

---

### Задачи

#### 2.1 SQLAlchemy модель Deal
**Файл:** `app/models/deal.py`

```python
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Deal(Base):
    """Сущность Сделка в базе данных"""
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default="new", index=True)  # new, negotiation, won, lost
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Связи
    client = relationship("Client", back_populates="deals")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_deals")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_deals")
    tasks = relationship("Task", back_populates="deal", cascade="all, delete-orphan")
```

**Наводящий вопрос:** Как хранить сумму — Integer или Decimal?
**Подсказка:** Используй Numeric(12, 2) для денежных сумм

**Ожидаемый результат:** Модель создана

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Настроены ForeignKey на clients и users
- [ ] Настроены relationship для доступа к объектам

---

#### 2.2 Pydantic DTO для Deal
**Файл:** `app/dtos/deal.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class DealStatus(str, Enum):
    """Статусы сделки"""
    NEW = "new"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class DealCreateDTO(BaseModel):
    """DTO для создания сделки"""
    title: str = Field(..., min_length=1, max_length=255)
    client_id: int
    amount: float = Field(..., ge=0)
    status: DealStatus = DealStatus.NEW
    assigned_to: int | None = None

class DealUpdateDTO(BaseModel):
    """DTO для обновления сделки"""
    title: str | None = Field(None, min_length=1, max_length=255)
    client_id: int | None = None
    amount: float | None = Field(None, ge=0)
    status: DealStatus | None = None
    assigned_to: int | None = None

class DealResponseDTO(BaseModel):
    """DTO для ответа"""
    id: int
    title: str
    client_id: int
    amount: float
    status: DealStatus
    created_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    
    class Config:
        from_attributes = True
```

**Ожидаемый результат:** DTO готовы

---

#### 2.3 Сервис для Deal
**Файл:** `app/services/deal_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.deal import Deal
from app.dtos.deal import DealCreateDTO, DealUpdateDTO, DealStatus
from typing import List, Optional, Tuple
from datetime import datetime

class DealService:
    """Сервис для работы со сделками"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, deal_data: DealCreateDTO, created_by: int) -> Deal:
        """Создать новую сделку"""
        deal = Deal(
            **deal_data.model_dump(),
            created_by=created_by
        )
        self.db.add(deal)
        await self.db.commit()
        await self.db.refresh(deal)
        return deal
    
    async def get_by_id(self, deal_id: int) -> Optional[Deal]:
        """Получить сделку по ID"""
        result = await self.db.execute(
            select(Deal).where(Deal.id == deal_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: DealStatus | None = None,
        client_id: int | None = None,
        assigned_to: int | None = None
    ) -> Tuple[List[Deal], int]:
        """Получить все сделки с фильтрацией"""
        query = select(Deal)
        count_query = select(func.count(Deal.id))
        
        # Фильтры
        if status:
            query = query.where(Deal.status == status)
            count_query = count_query.where(Deal.status == status)
        
        if client_id:
            query = query.where(Deal.client_id == client_id)
            count_query = count_query.where(Deal.client_id == client_id)
        
        if assigned_to:
            query = query.where(Deal.assigned_to == assigned_to)
            count_query = count_query.where(Deal.assigned_to == assigned_to)
        
        # Получаем общее количество
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Пагинация и сортировка
        query = query.offset(skip).limit(limit).order_by(Deal.created_at.desc())
        result = await self.db.execute(query)
        deals = list(result.scalars().all())
        
        return deals, total
    
    async def update(
        self,
        deal_id: int,
        deal_data: DealUpdateDTO,
        user_id: int
    ) -> Optional[Deal]:
        """Обновить сделку"""
        deal = await self.get_by_id(deal_id)
        if not deal:
            return None
        
        update_data = deal_data.model_dump(exclude_unset=True)
        
        # Автоматическая установка closed_at при закрытии сделки
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status in [DealStatus.WON, DealStatus.LOST] and deal.closed_at is None:
                deal.closed_at = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(deal, field, value)
        
        await self.db.commit()
        await self.db.refresh(deal)
        return deal
    
    async def delete(self, deal_id: int) -> bool:
        """Удалить сделку"""
        deal = await self.get_by_id(deal_id)
        if not deal:
            return False
        
        await self.db.delete(deal)
        await self.db.commit()
        return True
    
    async def get_stats(self) -> dict:
        """Получить статистику по сделкам"""
        # Общее количество
        total_result = await self.db.execute(select(func.count(Deal.id)))
        total = total_result.scalar()
        
        # По статусам
        stats = {}
        for status in DealStatus:
            result = await self.db.execute(
                select(func.count(Deal.id)).where(Deal.status == status.value)
            )
            stats[status.value] = result.scalar()
        
        # Сумма выигранных
        won_result = await self.db.execute(
            select(func.sum(Deal.amount)).where(Deal.status == DealStatus.WON.value)
        )
        won_amount = won_result.scalar() or 0
        
        return {
            "total": total,
            "by_status": stats,
            "won_amount": float(won_amount)
        }
```

**Наводящий вопрос:** Как автоматически устанавливать дату закрытия?
**Подсказка:** При обновлении проверяй, если новый статус WON или LOST → установи current datetime в closed_at

**Ожидаемый результат:** Сервис создан

---

#### 2.4 Роутер для Deal
**Файл:** `app/routes/deals.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.deal import DealCreateDTO, DealUpdateDTO, DealResponseDTO, DealStatus
from app.services.deal_service import DealService
from app.models.user import User
from app.deps.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/deals", tags=["Deals"])

@router.get("/", response_model=List[DealResponseDTO])
async def get_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: DealStatus | None = Query(None),
    client_id: int | None = Query(None),
    assigned_to: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список сделок с фильтрацией"""
    service = DealService(db)
    deals, total = await service.get_all(
        skip=skip,
        limit=limit,
        status=status,
        client_id=client_id,
        assigned_to=assigned_to
    )
    return deals

@router.post("/", response_model=DealResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новую сделку"""
    service = DealService(db)
    deal = await service.create(deal_data, created_by=current_user.id)
    return deal

@router.get("/{deal_id}", response_model=DealResponseDTO)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить сделку по ID"""
    service = DealService(db)
    deal = await service.get_by_id(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

@router.put("/{deal_id}", response_model=DealResponseDTO)
async def update_deal(
    deal_id: int,
    deal_data: DealUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить сделку"""
    service = DealService(db)
    deal = await service.update(deal_id, deal_data, user_id=current_user.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить сделку"""
    service = DealService(db)
    success = await service.delete(deal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deal not found")
```

**Ожидаемый результат:** CRUD операции работают

**Критерии приёмки:**
- [ ] GET /api/deals возвращает список с фильтрацией
- [ ] POST /api/deals создаёт сделку
- [ ] GET /api/deals/{id} возвращает сделку
- [ ] PUT /api/deals/{id} обновляет сделку
- [ ] DELETE /api/deals/{id} удаляет сделку
- [ ] При закрытии сделки автоматически ставится closed_at

---

## Этап 3: Расширенная функциональность (Неделя 9-10)

### Задачи

#### 3.1 Статистика сделок
**Бонусная задача:**

Добавить эндпоинт для получения статистики:
```python
@router.get("/stats")
async def get_deal_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить статистику по сделкам"""
    service = DealService(db)
    return await service.get_stats()
```

**Ожидаемый результат:** Статистика работает

---

## Этап 4: Интеграция (Неделя 14-15)

### Задачи

#### 4.1 Тестирование с фронтендом
**Взаимодействие с Александром:**

1. Предоставить документацию по API
2. Протестировать Kanban доску
3. Исправить найденные баги

**Ожидаемый результат:** Frontend и Backend работают вместе

---

## Git Workflow

### Ветка
```
feature/deals-evelina
```

### Коммиты
```
feat: add Deal model
feat: add Deal DTOs with status enum
feat: add Deal service with business logic
feat: add CRUD endpoints for deals
feat: add auto close date on status change
```

### Перед слиянием
```bash
git fetch origin
git rebase origin/main
git push origin feature/deals-evelina
```

---

## Взаимодействие с командой

### С Даниилом (Backend Lead)
- Консультации по архитектуре
- Помощь с SQLAlchemy
- Проверка кода перед коммитом
- Проверка DDD структуры

### С Соней (Backend)
- Согласование связей между Client и Deal
- Тестирование совместной работы

### С Александром (Frontend)
- Согласование формата данных для Kanban
- Консультации по интеграции

---

## Критерии приёмки

- [ ] Модель Deal создана
- [ ] Pydantic DTO работают валидацию
- [ ] Сервис содержит бизнес-логику
- [ ] Все CRUD операции работают
- [ ] Фильтрация по статусу работает
- [ ] При закрытии сделки автоматически ставится closed_at
- [ ] Все операции требуют авторизацию
- [ ] Документация в коде (docstrings)
- [ ] DDD структура соблюдена

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Модель Deal | Неделя 7-8 | |
| DTO и Сервис | Неделя 7-8 | |
| CRUD операции | Неделя 7-8 | |
| Статистика | Неделя 9-10 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Даниилу (Backend Lead)*
