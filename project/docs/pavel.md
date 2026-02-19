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

## DDD Архитектура

### Структура файлов для задач

```
app/
├── models/
│   ├── task.py          # SQLAlchemy модель задачи
│   └── interaction.py   # SQLAlchemy модель взаимодействия
├── dtos/
│   ├── task.py         # Pydantic DTO для задач
│   └── interaction.py   # Pydantic DTO для взаимодействий
├── services/
│   ├── task_service.py       # Бизнес-логика задач
│   ├── interaction_service.py # Бизнес-логика взаимодействий
│   └── dashboard_service.py  # Бизнес-логика дашборда
└── routes/
    ├── tasks.py       # HTTP эндпоинты задач
    ├── interactions.py # HTTP эндпоинты взаимодействий
    └── dashboard.py   # HTTP эндпоинты дашборда
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
- DTO клиента и сделки
- Сервисы клиента и сделки
- Как работают роутеры
- Как настроена аутентификация

**Ожидаемый результат:** Понимание DDD архитектуры проекта

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

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Task(Base):
    """Сущность Задача в базе данных"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium", index=True)  # low, medium, high
    status = Column(String(20), default="todo", index=True)  # todo, in_progress, done
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="tasks")
    deal = relationship("Deal", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
```

**Наводящий вопрос:** Зачем нужны поля client_id и deal_id nullable?
**Подсказка:** Задача может быть не привязана ни к клиенту, ни к сделке

**Ожидаемый результат:** Модель создана

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Настроены ForeignKey
- [ ] Поля nullable правильно настроены

---

#### 2.2 Pydantic DTO для Task
**Файл:** `app/dtos/task.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    """Приоритеты задач"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    """Статусы задач"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskCreateDTO(BaseModel):
    """DTO для создания задачи"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    client_id: int | None = None
    deal_id: int | None = None
    assigned_to: int
    due_date: datetime | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO

class TaskUpdateDTO(BaseModel):
    """DTO для обновления задачи"""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    client_id: int | None = None
    deal_id: int | None = None
    assigned_to: int | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None

class TaskResponseDTO(BaseModel):
    """DTO для ответа"""
    id: int
    title: str
    description: str | None
    client_id: int | None
    deal_id: int | None
    assigned_to: int
    due_date: datetime | None
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

**Ожидаемый результат:** DTO готовы

---

#### 2.3 Сервис для Task
**Файл:** `app/services/task_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.task import Task
from app.dtos.task import TaskCreateDTO, TaskUpdateDTO, TaskPriority, TaskStatus
from typing import List, Optional, Tuple
from datetime import datetime

class TaskService:
    """Сервис для работы с задачами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, task_data: TaskCreateDTO) -> Task:
        """Создать новую задачу"""
        task = Task(**task_data.model_dump())
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Получить задачу по ID"""
        result = await self.db.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TaskStatus | None = None,
        assigned_to: int | None = None,
        priority: TaskPriority | None = None
    ) -> Tuple[List[Task], int]:
        """Получить все задачи с фильтрацией"""
        query = select(Task)
        count_query = select(func.count(Task.id))
        
        if status:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)
        
        if assigned_to:
            query = query.where(Task.assigned_to == assigned_to)
            count_query = count_query.where(Task.assigned_to == assigned_to)
        
        if priority:
            query = query.where(Task.priority == priority)
            count_query = count_query.where(Task.priority == priority)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.offset(skip).limit(limit).order_by(Task.due_date.asc().nullslast())
        result = await self.db.execute(query)
        tasks = list(result.scalars().all())
        
        return tasks, total
    
    async def update(
        self,
        task_id: int,
        task_data: TaskUpdateDTO
    ) -> Optional[Task]:
        """Обновить задачу"""
        task = await self.get_by_id(task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def delete(self, task_id: int) -> bool:
        """Удалить задачу"""
        task = await self.get_by_id(task_id)
        if not task:
            return False
        
        await self.db.delete(task)
        await self.db.commit()
        return True
    
    async def get_overdue(self) -> List[Task]:
        """Получить просроченные задачи"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Task)
            .where(
                Task.due_date < now,
                Task.status != TaskStatus.DONE
            )
            .order_by(Task.due_date.asc())
        )
        return list(result.scalars().all())
```

**Ожидаемый результат:** Сервис создан

---

#### 2.4 Роутер для Task
**Файл:** `app/routes/tasks.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.task import TaskCreateDTO, TaskUpdateDTO, TaskResponseDTO, TaskStatus, TaskPriority
from app.services.task_service import TaskService
from app.models.user import User
from app.deps.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskResponseDTO])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: TaskStatus | None = Query(None),
    assigned_to: int | None = Query(None),
    priority: TaskPriority | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список задач с фильтрацией"""
    service = TaskService(db)
    tasks, total = await service.get_all(
        skip=skip,
        limit=limit,
        status=status,
        assigned_to=assigned_to,
        priority=priority
    )
    return tasks

@router.post("/", response_model=TaskResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новую задачу"""
    service = TaskService(db)
    task = await service.create(task_data)
    return task

@router.get("/{task_id}", response_model=TaskResponseDTO)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить задачу по ID"""
    service = TaskService(db)
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponseDTO)
async def update_task(
    task_id: int,
    task_data: TaskUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить задачу"""
    service = TaskService(db)
    task = await service.update(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить задачу"""
    service = TaskService(db)
    success = await service.delete(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
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

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Interaction(Base):
    """Сущность Взаимодействие в базе данных"""
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # call, meeting, email, note
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_internal = Column(Boolean, default=False)
    
    # Связи
    client = relationship("Client", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
```

**Ожидаемый результат:** Модель создана

---

#### 3.2 Pydantic DTO для Interaction
**Файл:** `app/dtos/interaction.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class InteractionType(str, Enum):
    """Типы взаимодействий"""
    CALL = "call"
    MEETING = "meeting"
    EMAIL = "email"
    NOTE = "note"

class InteractionCreateDTO(BaseModel):
    """DTO для создания взаимодействия"""
    client_id: int
    type: InteractionType
    description: str = Field(..., min_length=1)
    is_internal: bool = False

class InteractionResponseDTO(BaseModel):
    """DTO для ответа"""
    id: int
    client_id: int
    user_id: int
    type: InteractionType
    description: str
    created_at: datetime
    is_internal: bool
    
    class Config:
        from_attributes = True
```

---

#### 3.3 Сервис для Interaction
**Файл:** `app/services/interaction_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.interaction import Interaction
from app.dtos.interaction import InteractionCreateDTO
from typing import List, Optional

class InteractionService:
    """Сервис для работы с взаимодействиями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, interaction_data: InteractionCreateDTO, user_id: int) -> Interaction:
        """Создать новое взаимодействие"""
        interaction = Interaction(
            **interaction_data.model_dump(),
            user_id=user_id
        )
        self.db.add(interaction)
        await self.db.commit()
        await self.db.refresh(interaction)
        return interaction
    
    async def get_by_client(
        self,
        client_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Interaction]:
        """Получить историю взаимодействий клиента"""
        result = await self.db.execute(
            select(Interaction)
            .where(Interaction.client_id == client_id)
            .offset(skip)
            .limit(limit)
            .order_by(Interaction.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: int | None = None
    ) -> List[Interaction]:
        """Получить все взаимодействия"""
        query = select(Interaction).order_by(Interaction.created_at.desc())
        
        if client_id:
            query = query.where(Interaction.client_id == client_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
```

---

#### 3.4 Роутер для Interaction
**Файл:** `app/routes/interactions.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.interaction import InteractionCreateDTO, InteractionResponseDTO
from app.services.interaction_service import InteractionService
from app.models.user import User
from app.deps.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])

@router.get("/", response_model=List[InteractionResponseDTO])
async def get_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список взаимодействий"""
    service = InteractionService(db)
    interactions = await service.get_all(skip=skip, limit=limit, client_id=client_id)
    return interactions

@router.get("/client/{client_id}", response_model=List[InteractionResponseDTO])
async def get_client_interactions(
    client_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить историю взаимодействий с клиентом"""
    service = InteractionService(db)
    interactions = await service.get_by_client(client_id, skip=skip, limit=limit)
    return interactions

@router.post("/", response_model=InteractionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: InteractionCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать запись о взаимодействии"""
    service = InteractionService(db)
    interaction = await service.create(interaction_data, user_id=current_user.id)
    return interaction
```

---

## Этап 4: Дашборд (Неделя 13)

### Задачи

#### 4.1 Сервис для Дашборда
**Файл:** `app/services/dashboard_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.client import Client
from app.models.deal import Deal
from app.models.task import Task
from app.dtos.deal import DealStatus
from app.dtos.task import TaskStatus
from datetime import datetime

class DashboardService:
    """Сервис для получения статистики дашборда"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_stats(self) -> dict:
        """Получить статистику для дашборда"""
        # Всего клиентов
        clients_result = await self.db.execute(select(func.count(Client.id)))
        total_clients = clients_result.scalar()
        
        # Активных сделок (new, negotiation)
_result = await self.db.execute(
                   active_deals select(func.count(Deal.id)).where(
                Deal.status.in_([DealStatus.NEW.value, DealStatus.NEGOTIATION.value])
            )
        )
        active_deals = active_deals_result.scalar()
        
        # Выигранных сделок
        won_deals_result = await self.db.execute(
            select(func.count(Deal.id)).where(Deal.status == DealStatus.WON.value)
        )
        won_deals = won_deals_result.scalar()
        
        # Сумма выигранных сделок
        won_amount_result = await self.db.execute(
            select(func.sum(Deal.amount)).where(Deal.status == DealStatus.WON.value)
        )
        total_won_amount = float(won_amount_result.scalar() or 0)
        
        # Открытых задач
        open_tasks_result = await self.db.execute(
            select(func.count(Task.id)).where(Task.status != TaskStatus.DONE.value)
        )
        open_tasks = open_tasks_result.scalar()
        
        # Просроченных задач
        now = datetime.utcnow()
        overdue_result = await self.db.execute(
            select(func.count(Task.id)).where(
                Task.due_date < now,
                Task.status != TaskStatus.DONE.value
            )
        )
        overdue_tasks = overdue_result.scalar()
        
        return {
            "total_clients": total_clients,
            "active_deals": active_deals,
            "won_deals": won_deals,
            "total_won_amount": total_won_amount,
            "open_tasks": open_tasks,
            "overdue_tasks": overdue_tasks
        }
```

#### 4.2 Роутер для Дашборда
**Файл:** `app/routes/dashboard.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.models.user import User
from app.deps.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить статистику для дашборда"""
    service = DashboardService(db)
    return await service.get_stats()
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
feat: add Task DTOs
feat: add Task service with business logic
feat: add CRUD endpoints for tasks
feat: add Interaction model
feat: add Interaction DTOs
feat: add Interaction service
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
- Проверка DDD структуры

### С Соней и Эвелиной (Backend)
- Согласование связей между моделями

### С Александром (Frontend)
- Согласование формата данных для дашборда
- Консультации по интеграции

---

## Критерии приёмки

- [ ] Модель Task создана
- [ ] Модель Interaction создана
- [ ] Pydantic DTO работают валидацию
- [ ] Сервисы содержат бизнес-логику
- [ ] Все CRUD операции работают
- [ ] Фильтрация задач работает
- [ ] История взаимодействий клиента работает
- [ ] Дашборд возвращает статистику
- [ ] Все операции требуют авторизацию
- [ ] Документация в коде
- [ ] DDD структура соблюдена

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Модель Task | Неделя 9-10 | |
| DTO и Сервис | Неделя 9-10 | |
| CRUD операции | Неделя 9-10 | |
| Interaction | Неделя 11-12 | |
| Дашборд | Неделя 13 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Даниилу (Backend Lead)*
