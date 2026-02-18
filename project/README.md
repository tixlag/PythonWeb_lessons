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

## 2. База данных: Основные сущности

### 2.1 Схема данных

```
users (Пользователи системы)
├── id (PK)
├── username
├── email
├── hashed_password
├── full_name
├── role (admin/manager)
└── is_active

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

### 2.2 Взаимодействие сущностей

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

## 3. Структура API

### 3.1 Эндпоинты

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

## 4. Распределение задач

### 4.1 Backend-разработка

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
1. Pydantic модели для Client
2. SQLAlchemy модели для Client
3. CRUD операции для клиентов (Create, Read, Update, Delete)
4. Пагинация и фильтрация
5. Валидация данных

**Технические навыки для изучения:**
- Pydantic BaseModel
- SQLAlchemy relationship
- Query параметры

---

#### Эвелина (Backend Developer)

**Зона ответственности:** Сделки (Deals)

**Задачи:**
1. Pydantic модели для Deal
2. SQLAlchemy модели для Deal
3. CRUD операции для сделок (Create, Read, Update, Delete)
4. Связь с клиентами
5. Статусы сделок

**Технические навыки для изучения:**
- Enum для статусов
- ForeignKey relationships
- Cascade delete

---

#### Павел (Backend Developer)

**Зона ответственности:** Задачи и взаимодействия

**Задачи:**
1. Pydantic модели для Task
2. SQLAlchemy модели для Task
3. CRUD операции для задач
4. Модель Interaction
5. Dashboard статистика

**Технические навыки для изучения:**
- Optional поля в Pydantic
- Aggregation запросы
- Datetime handling

---

### 4.2 Frontend-разработка

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

### 4.3 DevOps

#### Николай (DevOps Engineer)

**Зона ответственности:** Инфраструктура и CI/CD

**Задачи:**
1. Docker Compose настройка
2. Nginx конфигурация
3. Скрипты миграции
4. Мониторинг и логирование
5. Деплой

---

## 5. Методические указания: FastAPI для начинающих

### 5.1 Основы FastAPI

FastAPI — это современный веб-фреймворк для Python с автоматической документацией.

**Пример аналогии (не решение задачи!):**

Представь, что ты пишешь блог. Вот как выглядит базовая структура:

```python
# Аналогия: Книжная полка (сущность "Книга")
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Модель данных (как анкета для книги)
class BookCreate(BaseModel):
    title: str
    author: str
    pages: int
    published_year: int

# Хранилище в памяти (в реальном проекте — база данных)
books_db = []

# Роутер (стеллаж с книгами)
@app.post("/books/")
def create_book(book: BookCreate):
    books_db.append(book)
    return {"id": 1, "status": "created"}

@app.get("/books/")
def get_books():
    return books_db
```

**Наводящий вопрос:** Как бы ты описал структуру для "Клиента" вместо "Книги"? Какие поля нужны?

---

### 5.2 Роутинг в FastAPI

Роутинг определяет, какой код выполняется при обращении к определённому URL.

**Пример аналогии:**

```python
# Аналогия: Рецепт приготовления блюда
@app.get("/recipes/")           # GET - прочитать меню
def get_recipes():
    return ["Борщ", "Пельмени", "Оливье"]

@app.post("/recipes/")          # POST - добавить рецепт
def add_recipe(recipe: Recipe):
    return {"id": 1}

@app.get("/recipes/{recipe_id}") # GET с параметром
def get_recipe(recipe_id: int):
    return {"name": "Борщ", "id": recipe_id}

@app.put("/recipes/{recipe_id}") # PUT - обновить
def update_recipe(recipe_id: int, recipe: Recipe):
    return {"status": "updated"}

@app.delete("/recipes/{recipe_id}") # DELETE - удалить
def delete_recipe(recipe_id: int):
    return {"status": "deleted"}
```

**Подсказка:** Обрати внимание на декораторы `@app.get`, `@app.post`, `@app.put`, `@app.delete`. Каждый метод HTTP соответствует определённому действию.

---

### 5.3 Pydantic модели

Pydantic обеспечивает валидацию данных "на лету".

**Пример аналогии:**

```python
# Аналогия: Заявка на кредит в банке
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class LoanApplication(BaseModel):
    # Обязательные поля
    name: str = Field(..., min_length=2, max_length=100)
    amount: int = Field(..., gt=0)  # больше 0
    
    # Проверяемый email (автоматически!)
    email: EmailStr
    
    # Необязательное поле
    phone: Optional[str] = None
    
    # Значение по умолчанию
    priority: Priority = Priority.MEDIUM

# FastAPI автоматически:
# 1. Проверит типы данных
# 2. Валидирует email
# 3. Отклонит невалидные данные
# 4. Сгенерирует документацию
```

**Задание для понимания:** Какие поля должны быть у модели "Клиент"? Используй аналогию с банковской заявкой.

---

### 5.4 Зависимости (Depends)

`Depends` позволяет внедрять зависимости и переиспользовать код.

**Пример аналогии:**

```python
# Аналогия: Охранник на входе
from fastapi import Depends

# Функция проверки пропуска
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Здесь будет проверка токена
    return {"user_id": 1, "role": "manager"}

# Использование: охранник пропускает только с пропуском
@app.get("/protected-data/")
def get_protected_data(current_user = Depends(get_current_user)):
    return {"data": "secret", "by": current_user["user_id"]}

# Аналогия: Чтобы войти в здание, нужно пройти через охранника
# Чтобы получить данные — нужно пройти через get_current_user
```

**Подсказка:** `Depends` как передача аргументов в функцию, только автоматически от FastAPI.

---

### 5.5 Асинхронность

Асинхронность позволяет обрабатывать много запросов одновременно.

**Пример аналогии:**

```python
import asyncio

# Синхронно (последовательно): Покупатель стоит в очереди к каждому продавцу
def sync_shopping():
    item1 = buy_at_store("магазин1")  # ждём
    item2 = buy_at_store("магазин2")  # ждём
    item3 = buy_at_store("магазин3")  # ждём

# Асинхронно (параллельно): Один покупатель звонит всем трём сразу
async def async_shopping():
    # Создаём задачи
    task1 = asyncio.create_task(buy_at_store_async("магазин1"))
    task2 = asyncio.create_task(buy_at_store_async("магазин2"))
    task3 = asyncio.create_task(buy_at_store_async("магазин3"))
    
    # Ждём все результаты
    item1, item2, item3 = await asyncio.gather(task1, task2, task3)

# В FastAPI:
@app.get("/sync-endpoint/")        # Обычная функция
def sync_endpoint():
    return {"status": "ok"}

@app.get("/async-endpoint/")       # async функция
async def async_endpoint():
    await asyncio.sleep(1)  # не блокирует другие запросы
    return {"status": "ok"}
```

**Важно:** Работа с базой данных в FastAPI требует асинхронного подключения.

---

### 5.6 SQLAlchemy: Работа с базой данных

**Пример аналогии:**

```python
# Аналогия: Табель учёта работников
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String)
    
    # Связь: у одного начальника может быть много подчинённых
    tasks = relationship("Task", back_populates="worker")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    
    # Обратная связь
    worker = relationship("Worker", back_populates="tasks")

# Запросы:
# worker.tasks = все задачи работника
# task.worker = работник, которому принадлежит задача
```

---

## 6. Методические указания: Frontend (Vanilla JS)

### 6.1 Структура проекта

```
frontend/
├── index.html
├── style.css
├── app.js
├── api/
│   └── client.js
├── pages/
│   ├── login.html
│   ├── clients.html
│   ├── deals.html
│   └── tasks.html
└── components/
    ├── header.js
    └── modal.js
```

### 6.2 Работа с API

**Пример аналогии:**

```javascript
// Аналогия: Заказ еды в ресторане
const API_URL = "https://api.crm-system.com";

// GET - посмотреть меню
async function getClients() {
    const response = await fetch(`${API_URL}/clients/`, {
        headers: {
            "Authorization": `Bearer ${getToken()}`
        }
    });
    return response.json();
}

// POST - сделать заказ
async function createClient(clientData) {
    const response = await fetch(`${API_URL}/clients/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${getToken()}`
        },
        body: JSON.stringify(clientData)
    });
    return response.json();
}
```

---

## 7. Git Workflow

### 7.1 Правила работы с ветками

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

### 7.2 Алгоритм работы

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

## 8. Пошаговый план реализации

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

- [ ] Pydantic модели Client
- [ ] CRUD операции
- [ ] Пагинация

### Неделя 7-8: Backend - Deals & Tasks

- [ ] Модель Deal
- [ ] Модель Task
- [ ] Взаимосвязи

### Неделя 9-10: Frontend - Auth

- [ ] Страница входа
- [ ] Регистрация
- [ ] Token management

### Неделя 11-13: Frontend - UI

- [ ] Клиенты (список, форма)
- [ ] Сделки (Kanban доска)
- [ ] Задачи

### Неделя 14-15: Интеграция и тестирование

- [ ] Связка Frontend ↔ Backend
- [ ] Исправление багов
- [ ] UI/UX доработки

### Неделя 16: Деплой

- [ ] Docker production сборка
- [ ] Nginx настройка
- [ ] Презентация проекта

---

## 9. Критерии оценки

### Backend (40 баллов)
- [ ] Корректная работа API (10)
- [ ] Валидация данных (5)
- [ ] Обработка ошибок (5)
- [ ] Безопасность (5)
- [ ] Архитектура кода (5)
- [ ] Документация (5)
- [ ] Тесты (5)

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

## 10. Ресурсы для изучения

### FastAPI
- Официальная документация: https://fastapi.tiangolo.com/
- Русскоязычное руководство: https://fastapi-ru.tdetailed-1.gitbook.io/

### SQLAlchemy
- Документация: https://docs.sqlalchemy.org/

### Vanilla JS
- MDN Web Docs: https://developer.mozilla.org/ru/docs/Web/JavaScript

---

*Документ подготовлен для командного проекта студентов*
