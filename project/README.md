# CRM-система: Методические материалы для командного проекта

**Курс:** Разработка полноstack-приложений  
**Продолжительность:** 1 семестр (16 недель)  
**Состав команды:** 7 студентов + 1 преподаватель

---

## 1. Введение и цель проекта

### 1.1 Что такое CRM-система

CRM (Customer Relationship Management) — система управления взаимодействием с клиентами. В рамках данного проекта мы создадим упрощённую CRM для малого бизнеса, которая позволит:

- Управлять базой клиентов
- Отслеживать сделки и их статусы
- Назначать задачи сотрудникам
- Вести историю взаимодействий с клиентами

### 1.2 Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vanilla JS)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐    │
│  │ Clients │  │  Deals   │  │  Tasks  │  │   Dashboard     │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘    │
└───────┼────────────┼────────────┼────────────────┼─────────────┘
        │            │            │                │
        └────────────┴────────────┴────────────────┘
                               │
                      ┌────────▼────────┐
                      │   FastAPI API   │
                      │   (REST API)    │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │   PostgreSQL    │
                      └─────────────────┘
```

---

## 2. DDD Архитектура Backend

### 2.1 Структура проекта

Мы используем **Domain-Driven Design (DDD)** архитектуру с чётким разделением на слои:

```
backend/app/
├── __init__.py
├── main.py                 # FastAPI приложение (точка входа)
├── config.py               # Конфигурация приложения
├── database.py             # Подключение к БД
│
├── models/                 # СЛОЙ МОДЕЛЕЙ (Domain Layer)
│   ├── __init__.py
│   ├── user.py             # Модель пользователя
│   ├── client.py           # Модель клиента
│   ├── deal.py            # Модель сделки
│   ├── task.py            # Модель задачи
│   └── interaction.py     # Модель взаимодействия
│
├── dtos/                   # СЛОЙ DTO (Data Transfer Objects)
│   ├── __init__.py
│   ├── auth.py             # DTO для аутентификации
│   ├── client.py          # DTO для клиентов
│   ├── deal.py           # DTO для сделок
│   ├── task.py           # DTO для задач
│   └── interaction.py    # DTO для взаимодействий
│
├── services/               # СЛОЙ СЕРВИСОВ (Application Layer)
│   ├── __init__.py
│   ├── auth_service.py    # Бизнес-логика авторизации
│   ├── client_service.py  # Бизнес-логика клиентов
│   ├── deal_service.py   # Бизнес-логика сделок
│   ├── task_service.py   # Бизнес-логика задач
│   └── dashboard_service.py # Бизнес-логика дашборда
│
└── routes/                 # СЛОЙ ROUTES (Presentation Layer)
    ├── __init__.py
    ├── auth.py            # HTTP эндпоинты авторизации
    ├── clients.py        # HTTP эндпоинты клиентов
    ├── deals.py         # HTTP эндпоинты сделок
    ├── tasks.py        # HTTP эндпоинты задач
    ├── interactions.py # HTTP эндпоинты взаимодействий
    └── dashboard.py    # HTTP эндпоинты дашборда
```

### 2.2 Слои архитектуры

#### Слой Models (Domain Layer)
**Назначение:** Определение сущностей базы данных с помощью SQLAlchemy

**Пример модели:**
```python
# app/models/client.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Client(Base):
    """Сущность Клиент в базе данных"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    creator = relationship("User", back_populates="clients")
    deals = relationship("Deal", back_populates="client")
    tasks = relationship("Task", back_populates="client")
    interactions = relationship("Interaction", back_populates="client")
```

#### Слой DTO (Data Transfer Objects)
**Назначение:** Pydantic модели для валидации данных при передаче между слоями

**Пример DTO:**
```python
# app/dtos/client.py
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

#### Слой Services (Application Layer)
**Назначение:** Бизнес-логика приложения

**Пример сервиса:**
```python
# app/services/client_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.client import Client
from app.dtos.client import ClientCreateDTO, ClientUpdateDTO
from typing import List, Optional

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
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Получить всех клиентов"""
        result = await self.db.execute(
            select(Client).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(self, client_id: int, client_data: ClientUpdateDTO) -> Optional[Client]:
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

#### Слой Routes (Presentation Layer)
**Назначение:** HTTP эндпоинты (API роутеры)

**Пример роутера:**
```python
# app/routes/clients.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.client import ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO
from app.services.client_service import ClientService
from app.models.user import User
from app.routes.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/clients", tags=["Clients"])

@router.get("/", response_model=List[ClientResponseDTO])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список всех клиентов"""
    service = ClientService(db)
    clients = await service.get_all(skip=skip, limit=limit)
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

---

## 3. База данных: Основные сущности

### 3.1 Схема данных

```
users (Пользователи системы)
├── id (PK)
├── username
├── email
├── hashed_password
├── full_name
├── role (admin/manager)
├── is_active
├── created_at
└── updated_at

clients (Клиенты)
├── id (PK)
├── name (название компании или ФИО)
├── email
├── phone
├── company_name
├── address
├── notes
├── created_by (FK → users)
├── created_at
└── updated_at

deals (Сделки)
├── id (PK)
├── title
├── client_id (FK → clients)
├── amount
├── status (new/negotiation/won/lost)
├── created_by (FK → users)
├── assigned_to (FK → users)
├── created_at
├── updated_at
└── closed_at

tasks (Задачи)
├── id (PK)
├── title
├── description
├── client_id (FK → clients, nullable)
├── deal_id (FK → deals, nullable)
├── assigned_to (FK → users)
├── due_date
├── priority (low/medium/high)
├── status (todo/in_progress/done)
├── created_at
└── updated_at

interactions (История взаимодействий)
├── id (PK)
├── client_id (FK → clients)
├── user_id (FK → users)
├── type (call/meeting/email/note)
├── description
├── created_at
└── is_internal (boolean - только для сотрудников)
```

### 3.2 Взаимодействие сущностей

```
User ─────┬─────► creates ───► Client
          │
          ├─────► creates ───► Deal
          │          │
          │          └─────► belongs_to ───► Client
          │
          ├─────► assigned_to ──► Task
          │          │
          │          └─────► related_to ──► Client/Deal
          │
          └─────► creates ──► Interaction ──► Client
```

---

## 4. Структура API

### 4.1 Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| **Auth** |||
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Вход (JWT) |
| GET | /api/auth/me | Текущий пользователь |
| **Clients** |||
| GET | /api/clients | Список клиентов |
| POST | /api/clients | Создать клиента |
| GET | /api/clients/{id} | Получить клиента |
| PUT | /api/clients/{id} | Обновить клиента |
| DELETE | /api/clients/{id} | Удалить клиента |
| **Deals** |||
| GET | /api/deals | Список сделок |
| POST | /api/deals | Создать сделку |
| GET | /api/deals/{id} | Получить сделку |
| PUT | /api/deals/{id} | Обновить сделку |
| DELETE | /api/deals/{id} | Удалить сделку |
| **Tasks** |||
| GET | /api/tasks | Список задач |
| POST | /api/tasks | Создать задачу |
| GET | /api/tasks/{id} | Получить задачу |
| PUT | /api/tasks/{id} | Обновить задачу |
| DELETE | /api/tasks/{id} | Удалить задачу |
| **Interactions** |||
| GET | /api/clients/{id}/interactions | История клиента |
| POST | /api/interactions | Создать запись |
| **Dashboard** |||
| GET | /api/dashboard/stats | Статистика |

---

## 5. Распределение задач

### 5.1 Backend-разработка

#### Даниил (Backend Lead)

**Зона ответственности:** Аутентификация и авторизация

**Задачи:**
1. Настройка проекта FastAPI
2. Подключение PostgreSQL через SQLAlchemy
3. Регистрация и вход (JWT токены)
4. Защищённые роуты
5. Миграции Alembic

**Технические навыки для изучения:**
- HTTP Bearer tokens
- Password hashing (passlib)
- Depends для auth

---

#### Соня (Backend Developer)

**Зона ответственности:** Клиенты (Clients CRUD)

**Задачи:**
1. SQLAlchemy модель Client
2. Pydantic DTO для Client
3. Сервис для Client (бизнес-логика)
4. CRUD роутеры для клиентов
5. Пагинация и фильтрация

**Технические навыки для изучения:**
- Pydantic BaseModel
- SQLAlchemy relationship
- Query параметры

---

#### Эвелина (Backend Developer)

**Зона ответственности:** Сделки (Deals)

**Задачи:**
1. SQLAlchemy модель Deal
2. Pydantic DTO для Deal
3. Сервис для Deal
4. CRUD роутеры для сделок
5. Статусы сделок

**Технические навыки для изучения:**
- Enum для статусов
- ForeignKey relationships
- Cascade delete

---

#### Павел (Backend Developer)

**Зона ответственности:** Задачи и взаимодействия

**Задачи:**
1. SQLAlchemy модель Task
2. Pydantic DTO для Task
3. Сервис для Task
4. Модель Interaction
5. Dashboard статистика

**Технические навыки для изучения:**
- Optional поля в Pydantic
- Aggregation запросы
- Datetime handling

---

### 5.2 Frontend-разработка

#### Дмитрий (Frontend Lead)

**Зона ответственности:** Архитектура фронтенда и авторизация

**Задачи:**
1. Структура проекта
2. Стилизация (CSS)
3. Login/Register страницы
4. Token management
5. Protected routes

---

#### Иван (Frontend Developer)

**Зона ответственности:** Клиенты

**Задачи:**
1. Страница списка клиентов
2. Форма создания/редактирования
3. Поиск и фильтрация
4. Просмотр карточки клиента

---

#### Александр (Frontend Developer)

**Зона ответственности:** Сделки и задачи

**Задачи:**
1. Доска сделок (Kanban)
2. Страница задач
3. Модальные окна
4. Дашборд со статистикой

---

### 5.3 DevOps

#### Николай (DevOps Engineer)

**Зона ответственности:** Инфраструктура и CI/CD

**Задачи:**
1. Docker Compose настройка
2. Nginx конфигурация
3. Скрипты миграции
4. Мониторинг и логирование
5. Деплой

---

## 6. Git Workflow

### 6.1 Правила работы с ветками

```
main (стабильная версия)
  │
  ├── feature/auth-daniil
  │     │
  │     └── commit: add login endpoint
  │     └── commit: add JWT tokens
  │     └── commit: add register endpoint
  │
  ├── feature/clients-sonya
  │
  ├── feature/deals-evelina
  │
  ├── feature/tasks-pavel
  │
  ├── feature/frontend-login-dmitry
  │
  ├── feature/frontend-clients-ivan
  │
  ├── feature/frontend-deals-alexander
  │
  └── infrastructure-docker-nikolai
```

### 6.2 Алгоритм работы

1. **Создание ветки:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/task-description
   ```

2. **Работа с кодом:**
   ```bash
   git add .
   git commit -m "feat: add client model"
   ```

3. **Перед слиянием:**
   ```bash
   git fetch origin
   git rebase origin/main
   # Разрешить конфликты если есть
   ```

4. **Создание Pull Request:**
   - Название: краткое описание
   - Описание: что сделано
   - Reviewer: преподаватель

---

## 7. Пошаговый план реализации

### Неделя 1-2: Подготовка

- [x] Создание репозитория
- [ ] Настройка Docker Compose
- [ ] Структура проекта Backend
- [ ] Структура проекта Frontend

### Неделя 3-4: Backend - Auth

- [ ] Настройка SQLAlchemy
- [ ] Модели User
- [ ] JWT аутентификация
- [ ] Тестирование эндпоинтов

### Неделя 5-6: Backend - Clients

- [ ] DTO модель Client
- [ ] Сервис для Client
- [ ] CRUD операции
- [ ] Пагинация

### Неделя 7-8: Backend - Deals

- [ ] Модель Deal
- [ ] DTO для Deal
- [ ] Сервис для Deal
- [ ] CRUD операции

### Неделя 9-10: Backend - Tasks & Dashboard

- [ ] Модель Task
- [ ] DTO для Task
- [ ] Сервис для Task
- [ ] Модель Interaction
- [ ] Dashboard статистика

### Неделя 11-12: Frontend - Auth

- [ ] Страница входа
- [ ] Регистрация
- [ ] Token management

### Неделя 13-14: Frontend - UI

- [ ] Клиенты (список, форма)
- [ ] Сделки (Kanban доска)
- [ ] Задачи

### Неделя 15-16: Интеграция и Деплой

- [ ] Связка Frontend ↔ Backend
- [ ] Исправление багов
- [ ] Docker production сборка
- [ ] Nginx настройка
- [ ] Презентация проекта

---

## 8. Критерии оценки

### Backend (40 баллов)
- [ ] Корректная работа API (10)
- [ ] DDD архитектура (10)
- [ ] Валидация данных через DTO (5)
- [ ] Бизнес-логика в сервисах (5)
- [ ] Обработка ошибок (5)
- [ ] Безопасность (5)

### Frontend (40 баллов)
- [ ] Функциональность (10)
- [ ] UI/UX (10)
- [ ] Асинхронные запросы (5)
- [ ] Обработка ошибок (5)
- [ ] Код качество (5)
- [ ] Адаптивность (5)

### DevOps (20 баллов)
- [ ] Docker настройка (5)
- [ ] Nginx конфигурация (5)
- [ ] CI/CD (5)
- [ ] Документация (5)

---

## 9. Ресурсы для изучения

### FastAPI
- Официальная документация: https://fastapi.tiangolo.com/
- Русскоязычное руководство: https://fastapi-ru.tdetailed-1.gitbook.io/

### SQLAlchemy
- Документация: https://docs.sqlalchemy.org/

### Pydantic
- Документация: https://docs.pydantic.dev/

### DDD Architecture
- Статьи о Domain-Driven Design для Python

### Vanilla JS
- MDN Web Docs: https://developer.mozilla.org/ru/docs/Web/JavaScript

---

*Документ подготовлен для командного проекта студентов*
