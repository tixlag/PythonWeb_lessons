# Инструкция для Backend Developer — Соня

**Роль:** Backend Developer  
**Зона ответственности:** CRUD операции для клиентов (Clients)  
**Стек:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic

---

## Общие обязанности

1. Реализация API для сущности "Клиент"
2. Работа с базой данных
3. Валидация входных данных через DTO
4. Бизнес-логика в сервисах
5. Написание документации для своего API
6. Взаимодействие с Frontend (Иван)

---

## DDD Архитектура

### Структура файлов для клиентов

```
app/
├── models/
│   └── client.py          # SQLAlchemy модель
├── dtos/
│   └── client.py         # Pydantic DTO
├── services/
│   └── client_service.py # Бизнес-логика
└── routes/
    └── clients.py       # HTTP эндпоинты
```

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Настройка рабочего окружения
**Инструменты:** Git, Python, VS Code

**Задачи:**
1. Клонировать репозиторий
2. Создать ветку: `git checkout -b feature/clients-sonya`
3. Установить зависимости: `pip install -r requirements.txt`
4. Проверить, что проект запускается

**Ожидаемый результат:** Проект запускается локально

---

#### 1.2 Изучение структуры проекта
**Инструменты:** Изучение кода

**Изучить:**
- Как настроена база данных (спросить у Даниила)
- Как созданы модели (посмотреть у Даниила)
- Как созданы DTO (посмотреть у Даниила)
- Как созданы сервисы (посмотреть у Даниила)
- Как созданы роутеры (спросить у Даниила)

**Ожидаемый результат:** Понимание DDD архитектуры проекта

---

## Этап 2: Модель Client (Неделя 5-6)

### Задачи

#### 2.1 SQLAlchemy модель Client
**Файл:** `app/models/client.py`

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Client(Base):
    """Сущность Клиент в базе данных"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    creator = relationship("User", back_populates="clients")
    deals = relationship("Deal", back_populates="client", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="client", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="client", cascade="all, delete-orphan")
```

**Подсказка:** Не забудь добавить `index=True` для полей, по которым будет поиск

**Ожидаемый результат:** Модель создана

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Все поля соответствуют спецификации
- [ ] Настроен FK на users

---

#### 2.2 Pydantic DTO для Client
**Файл:** `app/dtos/client.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ClientCreateDTO(BaseModel):
    """DTO для создания клиента"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    company_name: str | None = Field(None, max_length=255)
    address: str | None = Field(None, max_length=500)
    notes: str | None = None

class ClientUpdateDTO(BaseModel):
    """DTO для обновления клиента (все поля опциональные)"""
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    company_name: str | None = Field(None, max_length=255)
    address: str | None = Field(None, max_length=500)
    notes: str | None = None

class ClientResponseDTO(BaseModel):
    """DTO для ответа (включает все поля)"""
    id: int
    name: str
    email: str | None
    phone: str | None
    company_name: str | None
    address: str | None
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

**Ожидаемый результат:** DTO готовы

---

#### 2.3 Сервис для Client
**Файл:** `app/services/client_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.client import Client
from app.dtos.client import ClientCreateDTO, ClientUpdateDTO
from typing import List, Optional, Tuple

class ClientService:
    """Сервис для работы с клиентами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, client_data: ClientCreateDTO, created_by: int) -> Client:
        """Создать нового клиента"""
        client = Client(
            **client_data.model_dump(),
            created_by=created_by
        )
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client
    
    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """Получить клиента по ID"""
        result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: str | None = None
    ) -> Tuple[List[Client], int]:
        """Получить всех клиентов с пагинацией и поиском"""
        # Базовый запрос
        query = select(Client)
        count_query = select(func.count(Client.id))
        
        # Поиск по имени или email
        if search:
            search_filter = or_(
                Client.name.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Получаем общее количество
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Пагинация
        query = query.offset(skip).limit(limit).order_by(Client.created_at.desc())
        result = await self.db.execute(query)
        clients = list(result.scalars().all())
        
        return clients, total
    
    async def update(
        self, 
        client_id: int, 
        client_data: ClientUpdateDTO
    ) -> Optional[Client]:
        """Обновить клиента"""
        client = await self.get_by_id(client_id)
        if not client:
            return None
        
        update_data = client_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        await self.db.commit()
        await self.db.refresh(client)
        return client
    
    async def delete(self, client_id: int) -> bool:
        """Удалить клиента"""
        client = await self.get_by_id(client_id)
        if not client:
            return False
        
        await self.db.delete(client)
        await self.db.commit()
        return True
```

**Ожидаемый результат:** Сервис создан

---

#### 2.4 Роутер для Client
**Файл:** `app/routes/clients.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.client import ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO
from app.services.client_service import ClientService
from app.models.user import User
from app.deps.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/clients", tags=["Clients"])

@router.get("/", response_model=List[ClientResponseDTO])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список клиентов с пагинацией и поиском"""
    service = ClientService(db)
    clients, total = await service.get_all(skip=skip, limit=limit, search=search)
    return clients

@router.post("/", response_model=ClientResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать нового клиента"""
    service = ClientService(db)
    client = await service.create(client_data, created_by=current_user.id)
    return client

@router.get("/{client_id}", response_model=ClientResponseDTO)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить клиента по ID"""
    service = ClientService(db)
    client = await service.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=ClientResponseDTO)
async def update_client(
    client_id: int,
    client_data: ClientUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить клиента"""
    service = ClientService(db)
    client = await service.update(client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить клиента"""
    service = ClientService(db)
    success = await service.delete(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
```

**Наводящий вопрос:** Как реализовать мягкое удаление (soft delete)?
**Подсказка:** Добавь поле `is_deleted` или `deleted_at` в модель и сервис

**Ожидаемый результат:** CRUD операции работают

**Критерии приёмки:**
- [ ] GET /api/clients возвращает список с пагинацией
- [ ] GET /api/clients?search=строка работает поиск
- [ ] POST /api/clients создаёт клиента
- [ ] GET /api/clients/{id} возвращает клиента
- [ ] PUT /api/clients/{id} обновляет клиента
- [ ] DELETE /api/clients/{id} удаляет клиента
- [ ] Требуется авторизация для всех операций

---

## Этап 3: Интеграция (Неделя 14-15)

### Задачи

#### 3.1 Тестирование с фронтендом
**Взаимодействие с Иваном:**

1. Предоставить документацию по API
2. Протестировать совместную работу
3. Исправить найденные баги

**Ожидаемый результат:** Frontend и Backend работают вместе

---

## Git Workflow

### Ветка
```
feature/clients-sonya
```

### Коммиты
```
feat: add Client model
feat: add Client DTOs
feat: add Client service
feat: add CRUD endpoints for clients
feat: add search and pagination
```

### Перед слиянием
```bash
git fetch origin
git rebase origin/main
git push origin feature/clients-sonya
```

---

## Взаимодействие с командой

### С Даниилом (Backend Lead)
- Консультации по архитектуре
- Помощь с SQLAlchemy
- Проверка кода перед коммитом
- Проверка DDD структуры

### С Иваном (Frontend)
- Согласование формата данных API
- Предоставление тестовых данных
- Консультации по интеграции

---

## Критерии приёмки

- [ ] Модель Client создана
- [ ] Pydantic DTO работают валидацию
- [ ] Сервис содержит бизнес-логику
- [ ] Все CRUD операции работают
- [ ] Пагинация работает
- [ ] Поиск по клиентам работает
- [ ] Все операции требуют авторизацию
- [ ] Документация в коде (docstrings)
- [ ] Нет паролей и секретов в коде
- [ ] DDD структура соблюдена

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Модель Client | Неделя 5-6 | |
| DTO и Сервис | Неделя 5-6 | |
| CRUD операции | Неделя 5-6 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Даниилу (Backend Lead)*
