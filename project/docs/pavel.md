# Инструкция для Backend Developer — Павел

**Роль:** Backend Developer  
**Зона ответственности:** Задачи (Tasks), Взаимодействия (Interactions), Дашборд  
**Стек:** Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic

---

## Общие обязанности

1. Реализация API для сущности "Задача" (Task)
2. Реализация API для истории взаимодействий (Interaction)
3. Создание дашборда со статистикой
4. Работа с датами
5. Взаимодействие с Frontend (Александр)

---

## Теоретический материал

### Optional поля в Pydantic

Поле может быть None (необязательное).

**Пример:**
```python
from typing import Optional

class Task(BaseModel):
    title: str  # Обязательное
    description: Optional[str] = None  # Необязательное, по умолчанию None
    due_date: Optional[datetime] = None
```

### Datetime в Python

Работа с датами и временем.

**Пример:**
```python
from datetime import datetime, timedelta

# Текущее время
now = datetime.utcnow()

# Дедлайн — через 7 дней
deadline = now + timedelta(days=7)

# Формат для JSON
deadline.isoformat()  # "2024-01-15T12:00:00"
```

### Aggregation запросы

Подсчёт статистики в базе данных.

**Пример:**
```python
from sqlalchemy import func, select

# Подсчёт количества
query = select(func.count()).select_from(Task)
result = await db.execute(query)
total = result.scalar()

# Подсчёт с условием
query = select(func.count()).select_from(Task).where(Task.status == "done")
done_count = await db.execute(query)
```

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Настройка рабочего окружения
**Инструменты:** Git, Python, VS Code

**Задачи:**
1. Клонировать репозиторий
2. Создать ветку: `git checkout -b feature/tasks-pavel`
3. Установить зависимости
4. Проверить, что проект запускается

**Ожидаемый результат:** Проект запускается локально

---

#### 1.2 Изучение структуры проекта
**Инструменты:** Изучение кода

**Изучить:**
- Модели Client и Deal (посмотреть у Сони и Эвелины)
- Как работают роутеры
- Как настроена аутентификация

**Ожидаемый результат:** Понимание архитектуры проекта

---

## Этап 2: Модель Task (Неделя 9-10)

### Теоретический материал

### Приоритеты задач

- **Low** — Низкий
- **Medium** — Средний  
- **High** — Высокий

### Статусы задач

- **todo** — К выполнению
- **in_progress** — В процессе
- **done** — Выполнено

---

### Задачи

#### 2.1 SQLAlchemy модель Task
**Файл:** `app/models/task.py`

**Поля:**
- id (Integer, PK)
- title (String, not null)
- description (Text, nullable)
- client_id (Integer, FK → clients.id, nullable)
- deal_id (Integer, FK → deals.id, nullable)
- assigned_to (Integer, FK → users.id)
- due_date (DateTime, nullable)
- priority (String) — low, medium, high
- status (String) — todo, in_progress, done
- created_at (DateTime)
- updated_at (DateTime)

```python
# Шаблон:
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="todo")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="tasks")
    deal = relationship("Deal", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to])
```

**Наводящий вопрос:** Зачем нужны поля client_id и deal_id nullable?
**Подсказка:** Задача может быть не привязана ни к клиенту, ни к сделке

**Ожидаемый результат:** Модель создана

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Настроены ForeignKey
- [ ] Поля nullable правильно настроены

---

#### 2.2 Pydantic схемы для Task
**Файл:** `app/schemas/task.py`

**Enums:**
```python
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
```

**Схемы:**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import TaskPriority, TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    client_id: int | None = None
    deal_id: int | None = None
    assigned_to: int
    due_date: datetime | None = None
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    client_id: int | None = None
    deal_id: int | None = None
    assigned_to: int | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None

class TaskResponse(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

**Ожидаемый результат:** Схемы готовы

---

#### 2.3 Роутер для Task
**Файл:** `app/routers/tasks.py`

**Эндпоинты:**

```python
router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

# GET / — получить все задачи
@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    status: TaskStatus | None = None,
    assigned_to: int | None = None,
    priority: TaskPriority | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список задач с фильтрацией"""

# POST / — создать задачу
@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новую задачу"""

# GET /{task_id} — получить задачу
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить задачу по ID"""

# PUT /{task_id} — обновить задачу
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить задачу"""

# DELETE /{task_id} — удалить задачу
@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить задачу"""
```

**Ожидаемый результат:** CRUD операции работают

---

## Этап 3: Модель Interaction (Неделя 11-12)

### Теоретический материал

### Типы взаимодействий

- **call** — Звонок
- **meeting** — Встреча
- **email** — Письмо
- **note** — Заметка

### Внутренние заметки

Поле `is_internal` — заметки только для сотрудников, не видны клиенту.

---

### Задачи

#### 3.1 SQLAlchemy модель Interaction
**Файл:** `app/models/interaction.py`

**Поля:**
- id (Integer, PK)
- client_id (Integer, FK → clients.id)
- user_id (Integer, FK → users.id)
- type (String) — call, meeting, email, note
- description (Text)
- created_at (DateTime)
- is_internal (Boolean, default=False)

```python
class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(20))  # call, meeting, email, note
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_internal = Column(Boolean, default=False)
    
    client = relationship("Client", back_populates="interactions")
    user = relationship("User")
```

**Ожидаемый результат:** Модель создана

---

#### 3.2 Pydantic схемы для Interaction
**Файл:** `app/schemas/interaction.py`

**Создай схемы:**

```python
from pydantic import BaseModel, Field
from datetime import datetime

class InteractionCreate(BaseModel):
    client_id: int
    type: str = Field(..., pattern="^(call|meeting|email|note)$")
    description: str
    is_internal: bool = False

class InteractionResponse(InteractionCreate):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

---

#### 3.3 Роутер для Interaction
**Файл:** `app/routers/interactions.py`

**Эндпоинты:**

```python
router = APIRouter(prefix="/api/interactions", tags=["Interactions"])

# GET / — получить все взаимодействия (для админа)
@router.get("/", response_model=list[InteractionResponse])
async def get_interactions(
    client_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список взаимодействий"""

# GET /client/{client_id} — получить историю клиента
@router.get("/client/{client_id}", response_model=list[InteractionResponse])
async def get_client_interactions(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю взаимодействий с клиентом"""

# POST / — создать взаимодействие
@router.post("/", response_model=InteractionResponse, status_code=201)
async def create_interaction(
    interaction_data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать запись о взаимодействии"""
```

---

## Этап 4: Дашборд (Неделя 13)

### Задачи

#### 4.1 Статистика для дашборда
**Файл:** `app/routers/dashboard.py`

**Эндпоинт:**
```python
@router.get("/api/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить статистику для дашборда"""
    
    # Вернуть:
    # - Всего клиентов
    # - Активных сделок
    # - Выигранных сделок (won)
    # - Выполненных задач
    # - Просроченных задач
    # - Сумма выигранных сделок
```

**Наводящий вопрос:** Как найти просроченные задачи?
**Подсказка:** Сравни due_date с текущим временем, если due_date < now и status != done

**Ожидаемый результат:** Дашборд работает

---

## Этап 5: Интеграция (Неделя 14-15)

### Задачи

#### 5.1 Тестирование с фронтендом
**Взаимодействие с Александром:**

1. Предоставить документацию по API
2. Протестировать совместную работу
3. Исправить найденные баги

---

## Git Workflow

### Ветка
```
feature/tasks-pavel
```

### Коммиты
```
feat: add Task model
feat: add Task schemas
feat: add CRUD endpoints for tasks
feat: add Interaction model
feat: add Interaction endpoints
feat: add dashboard statistics
```

### Перед слиянием
```bash
git fetch origin
git rebase origin/main
git push origin feature/tasks-pavel
```

---

## Взаимодействие с командой

### С Даниилом (Backend Lead)
- Консультации по архитектуре
- Проверка кода перед коммитом

### С Соней и Эвелиной (Backend)
- Согласование связей между моделями

### С Александром (Frontend)
- Согласование формата данных для дашборда
- Консультации по интеграции

---

## Критерии приёмки

- [ ] Модель Task создана
- [ ] Модель Interaction создана
- [ ] Все CRUD операции работают
- [ ] Фильтрация задач работает
- [ ] История взаимодействий клиента работает
- [ ] Дашборд возвращает статистику
- [ ] Все операции требуют авторизацию
- [ ] Документация в коде

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Модель Task | Неделя 9-10 | |
| CRUD операции | Неделя 9-10 | |
| Interaction | Неделя 11-12 | |
| Дашборд | Неделя 13 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Даниилу (Backend Lead)*
