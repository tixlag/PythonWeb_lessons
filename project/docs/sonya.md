# Инструкция для Backend Developer — Соня

**Роль:** Backend Developer  
**Зона ответственности:** CRUD операции для клиентов (Clients)  
**Стек:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic

---

## Общие обязанности

1. Реализация API для сущности "Клиент"
2. Работа с базой данных
3. Валидация входных данных
4. Написание документации для своего API
5. Взаимодействие с Frontend (Иван)

---

## Теоретический материал

### CRUD операции

CRUD расшифровывается как Create, Read, Update, Delete — четыре базовые операции с данными.

**Аналогия — Библиотека:**
- **Create (Создать):** Добавить новую книгу в каталог
- **Read (Прочитать):** Найти книгу в каталоге
- **Update (Обновить):** Изменить информацию о книге
- **Delete (Удалить):** Удалить книгу из каталога

### SQLAlchemy Relationships

Связи между таблицами в базе данных.

**Аналогия:**
```
Клиент (Client) → имеет → Много сделок (Deals)
```

В коде это выглядит так:
```python
# У клиента может быть много сделок
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    deals = relationship("Deal", back_populates="client")

# Сделка принадлежит одному клиенту
class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="deals")
```

### Пагинация

Пагинация — это разбиение большого списка на страницы.

**Аналогия:** Поиск в Google
- Показывается 10 результатов на странице
- Есть кнопки "Следующая", "Предыдущая"

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
- Как созданы другие модели (спросить у Даниила)
- Как созданы роутеры (спросить у Даниила)

**Ожидаемый результат:** Понимание архитектуры проекта

---

## Этап 2: Модель Client (Неделя 5-6)

### Теоретический материал

### Pydantic модели

Pydantic — это библиотека для валидации данных.

**Пример аналогии (не решение задачи!):**

Представь, что заполняешь анкету в банке:
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Анкета на кредит
class CreditApplication(BaseModel):
    # Обязательные поля
    full_name: str = Field(..., min_length=2, max_length=100)
    income: int = Field(..., gt=0)  # больше 0
    
    # Проверка email автоматически
    email: EmailStr
    
    # Необязательное поле
    phone: Optional[str] = None
```

**Задание:** Подумай, какие поля должны быть у "Клиента" в CRM?

---

### Задачи

#### 2.1 SQLAlchemy модель Client
**Файл:** `app/models/client.py`

**Поля:**
- id (Integer, PK)
- name (String, not null) — название компании или ФИО
- email (String, nullable)
- phone (String, nullable)
- company_name (String, nullable)
- address (String, nullable)
- notes (Text, nullable)
- created_by (Integer, FK → users.id)
- created_at (DateTime)
- updated_at (DateTime)

```python
# Шаблон (не готовое решение!):
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    # ... добавь остальные поля
    
    # Связи
    created_by_user = relationship("User", back_populates="clients")
```

**Подсказка:** Не забудь добавить `index=True` для полей, по которым будет поиск

**Ожидаемый результат:** Модель создана

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Все поля соответствуют спецификации
- [ ] Настроен FK на users

---

#### 2.2 Pydantic схемы для Client
**Файл:** `app/schemas/client.py`

**Создай 4 схемы:**

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# 1. При создании — какие данные нужны от клиента
class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    address: str | None = None
    notes: str | None = None

# 2. При обновлении — все поля необязательные
class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    # ... остальные поля

# 3. Полная информация о клиенте (для чтения)
class ClientResponse(ClientCreate):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 4. Для пагинации
class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    total: int
    page: int
    page_size: int
```

**Ожидаемый результат:** Схемы готовы

---

#### 2.3 Роутер для Client
**Файл:** `app/routers/clients.py`

**Эндпоинты:**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db
from app.models.user import User
from app.deps.auth import get_current_user

router = APIRouter(prefix="/api/clients", tags=["Clients"])

# GET / — получить список клиентов с пагинацией
@router.get("/", response_model=ClientListResponse)
async def get_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список клиентов с пагинацией и поиском"""
    # 1. Построить запрос к БД
    # 2. Добавить фильтр по search (поиск по name, email)
    # 3. Применить пагинацию (offset, limit)
    # 4. Вернуть результат

# POST / — создать клиента
@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать нового клиента"""
    # 1. Валидировать данные
    # 2. Создать объект модели
    # 3. Добавить created_by = current_user.id
    # 4. Сохранить в БД
    # 5. Вернуть созданного клиента

# GET /{client_id} — получить одного клиента
@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить клиента по ID"""
    # 1. Найти клиента в БД
    # 2. Если не найден — 404
    # 3. Вернуть клиента

# PUT /{client_id} — обновить клиента
@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить клиента"""
    # 1. Найти клиента
    # 2. Обновить только переданные поля
    # 3. Сохранить в БД

# DELETE /{client_id} — удалить клиента
@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить клиента"""
    # 1. Найти клиента
    # 2. Удалить из БД
```

**Наводящий вопрос:** Как реализовать мягкое удаление (soft delete)?
**Подсказка:** Добавь поле `is_deleted` или `deleted_at` в модель

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

#### 3.2 Оптимизация
**Если останется время:**

1. Добавить кэширование
2. Оптимизировать запросы к БД
3. Добавить больше индексов

---

## Git Workflow

### Ветка
```
feature/clients-sonya
```

### Коммиты
```
feat: add Client model
feat: add Client schemas
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

### С Иваном (Frontend)
- Согласование формата данных API
- Предоставление тестовых данных
- Консультации по интеграции

---

## Критерии приёмки

- [ ] Модель Client создана
- [ ] Pydantic схемы работают валидацию
- [ ] Все CRUD операции работают
- [ ] Пагинация работает
- [ ] Поиск по клиентам работает
- [ ] Все операции требуют авторизацию
- [ ] Документация в коде (docstrings)
- [ ] Нет паролей и секретов в коде

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Модель Client | Неделя 5-6 | |
| CRUD операции | Неделя 5-6 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Даниилу (Backend Lead)*
