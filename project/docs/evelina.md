# Инструкция для Backend Developer — Эвелина

**Роль:** Backend Developer  
**Зона ответственности:** Сделки (Deals)  
**Стек:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic

---

## Общие обязанности

1. Реализация API для сущности "Сделка" (Deal)
2. Работа с базой данных
3. Валидация входных данных
4. Управление статусами сделок
5. Взаимодействие с Frontend (Александр)

---

## Теоретический материал

### Enum в Python

Enum (перечисление) — это набор именованных констант.

**Пример аналогии (не решение задачи!):**

Представь статус заказа в магазине:
```python
from enum import Enum

class OrderStatus(str, Enum):
    """Статусы заказа"""
    PENDING = "pending"      # Ожидает
    PROCESSING = "processing" # В обработке
    SHIPPED = "shipped"      # Отправлен
    DELIVERED = "delivered"  # Доставлен
    CANCELLED = "cancelled"  # Отменён
```

**Зачем использовать Enum:**
- Ограничивает возможные значения
- Автодополнение в IDE
- Предотвращает опечатки

### Связи между таблицами (ForeignKey)

Связь "многие к одному" — у одной сущности может быть ссылка на другую.

**Аналогия:**
```
Сделка → относится к → Клиент
```

В коде:
```python
class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))  # Ссылка на клиента
    
    # Объект клиента для удобного доступа
    client = relationship("Client", back_populates="deals")
```

### Cascade Delete

Каскадное удаление — что происходит со связанными записями при удалении родительской.

**Аналогия:**
- Если удалить клиента → что делать с его сделками?
- Варианты: удалить все сделки, запретить удаление, обнулить ссылку

**В коде:**
```python
# Удалить все связанные сделки при удалении клиента
class Client(Base):
    deals = relationship("Deal", cascade="all, delete-orphan")
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
- Как работают роутеры (посмотреть у Даниила)
- Как настроена аутентификация

**Ожидаемый результат:** Понимание архитектуры проекта

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

**Поля:**
- id (Integer, PK)
- title (String, not null) — название сделки
- client_id (Integer, FK → clients.id)
- amount (Numeric/Integer) — сумма сделки
- status (String) — статус: new, negotiation, won, lost
- created_by (Integer, FK → users.id)
- assigned_to (Integer, FK → users.id) — ответственный
- created_at (DateTime)
- updated_at (DateTime)
- closed_at (DateTime, nullable)

```python
# Шаблон:
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    amount = Column(Numeric(12, 2), default=0)
    status = Column(String(50), default="new")  # new, negotiation, won, lost
    
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Связи
    client = relationship("Client", back_populates="deals")
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
```

**Наводящий вопрос:** Как хранить сумму — Integer или Decimal?
**Подсказка:** Используй Numeric(12, 2) для денежных сумм

**Ожидаемый результат:** Модель создана

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Настроены ForeignKey на clients и users
- [ ] Настроены relationship для доступа к объектам

---

#### 2.2 Pydantic схемы для Deal
**Файл:** `app/schemas/deal.py`

**Статусы:**
```python
from enum import Enum

class DealStatus(str, Enum):
    NEW = "new"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
```

**Схемы:**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import DealStatus

class DealCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    client_id: int
    amount: float = Field(..., ge=0)
    status: DealStatus = DealStatus.NEW
    assigned_to: int | None = None

class DealUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    client_id: int | None = None
    amount: float | None = Field(None, ge=0)
    status: DealStatus | None = None
    assigned_to: int | None = None

class DealResponse(DealCreate):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    
    class Config:
        from_attributes = True
```

**Ожидаемый результат:** Схемы готовы

---

#### 2.3 Роутер для Deal
**Файл:** `app/routers/deals.py`

**Эндпоинты:**

```python
router = APIRouter(prefix="/api/deals", tags=["Deals"])

# GET / — получить все сделки
@router.get("/", response_model=list[DealResponse])
async def get_deals(
    status: DealStatus | None = None,
    client_id: int | None = None,
    assigned_to: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список сделок с фильтрацией"""
    # 1. Построить базовый запрос
    # 2. Добавить фильтры по status, client_id, assigned_to
    # 3. Вернуть результат

# POST / — создать сделку
@router.post("/", response_model=DealResponse, status_code=201)
async def create_deal(
    deal_data: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новую сделку"""
    # 1. Проверить, что клиент существует
    # 2. Проверить, что assigned_to пользователь существует
    # 3. Создать сделку с created_by = current_user.id

# GET /{deal_id} — получить сделку
@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить сделку по ID"""

# PUT /{deal_id} — обновить сделку
@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    deal_data: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить сделку"""
    # 1. Найти сделку
    # 2. Если статус изменился на won/lost → установить closed_at

# DELETE /{deal_id} — удалить сделку
@router.delete("/{deal_id}", status_code=204)
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить сделку"""
```

**Наводящий вопрос:** Как автоматически устанавливать дату закрытия?
**Подсказка:** При обновлении проверяй, если новый статус WON или LOST → установи current datetime в closed_at

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
    # Вернуть:
    # - общее количество сделок
    # - количество по каждому статусу
    # - общую сумму выигранных сделок
    # - средний чек
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
feat: add Deal schemas with status enum
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

### С Соней (Backend)
- Согласование связей между Client и Deal
- Тестирование совместной работы

### С Александром (Frontend)
- Согласование формата данных для Kanban
- Консультации по интеграции

---

## Критерии приёмки

- [ ] Модель Deal создана
- [ ] Pydantic схемы работают валидацию
- [ ] Все CRUD операции работают
- [ ] Фильтрация по статусу работает
- [ ] При закрытии сделки自动чески ставится closed_at
- [ ] Все операции требуют авторизацию
- [ ] Документация в коде (docstrings)

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Модель Deal | Неделя 7-8 | |
| CRUD операции | Неделя 7-8 | |
| Статистика | Неделя 9-10 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Даниилу (Backend Lead)*
