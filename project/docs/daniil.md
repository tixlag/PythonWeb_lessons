# Инструкция для Backend Lead — Даниил

**Роль:** Backend Lead  
**Зона ответственности:** Аутентификация, авторизация, инфраструктура бэкенда  
**Стек:** Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT

---

## Общие обязанности

1. Координация работы бэкенд-команды (4 человека)
2. Принятие архитектурных решений
3. Настройка CI/CD для бэкенда
4. Проверка качества кода
5. Взаимодействие с DevOps (Николай) и Frontend Lead (Дмитрий)

---

## DDD Архитектура проекта

### Структура папок

```
backend/app/
├── main.py                 # Точка входа FastAPI
├── config.py              # Конфигурация
├── database.py            # Подключение к БД
│
├── models/                # Domain Layer - SQLAlchemy модели
│   ├── __init__.py
│   ├── user.py
│   ├── client.py
│   ├── deal.py
│   ├── task.py
│   └── interaction.py
│
├── dtos/                  # Data Transfer Objects - Pydantic модели
│   ├── __init__.py
│   ├── auth.py
│   ├── client.py
│   ├── deal.py
│   ├── task.py
│   └── interaction.py
│
├── services/              # Application Layer - Бизнес-логика
│   ├── __init__.py
│   ├── auth_service.py
│   ├── client_service.py
│   ├── deal_service.py
│   ├── task_service.py
│   └── dashboard_service.py
│
└── routes/                # Presentation Layer - HTTP эндпоинты
    ├── __init__.py
    ├── auth.py
    ├── clients.py
    ├── deals.py
    ├── tasks.py
    ├── interactions.py
    └── dashboard.py
```

---

## Этап 1: Подготовка окружения (Неделя 1-2)

### Задачи

#### 1.1 Создание структуры проекта

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа
│   ├── config.py            # Настройки приложения
│   ├── database.py          # Подключение к БД
│   ├── models/             # SQLAlchemy модели
│   ├── dtos/               # Pydantic DTO
│   ├── services/           # Бизнес-логика
│   └── routes/             # HTTP роутеры
├── requirements.txt
├── alembic.ini
└── .env.example
```

**Ожидаемый результат:** Базовая структура проекта создана и запускается без ошибок

**Критерии приёмки:**
- [ ] Приложение запускается командой `uvicorn app.main:app --reload`
- [ ] Доступна документация API по адресу `/docs`
- [ ] Файл `.env.example` содержит все необходимые переменные

**Инструменты:** VS Code, терминал, Git

---

#### 1.2 Настройка PostgreSQL и Docker Compose
**Взаимодействие с Николаем (DevOps):** Попроси его предоставить готовый `docker-compose.yml` с PostgreSQL

**Задачи:**
1. Настроить подключение к PostgreSQL через SQLAlchemy
2. Создать файл `.env` с переменными окружения
3. Протестировать подключение к БД

**Пример подключения:**
```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
```

**Ожидаемый результат:** Приложение подключается к PostgreSQL

**Критерии приёмки:**
- [ ] Нет ошибок подключения к БД
- [ ] Переменные DATABASE_URL настроены через `.env`

---

#### 1.3 Настройка Alembic для миграций
**Инструменты:** Alembic, SQLAlchemy

**Задачи:**
1. Инициализировать Alembic: `alembic init alembic`
2. Настроить `alembic.ini`
3. Создать первую миграцию для создания таблиц

**Ожидаемый результат:** Миграции работают, таблицы создаются

**Критерии приёмки:**
- [ ] Команда `alembic upgrade head` выполняется без ошибок
- [ ] Созданы таблицы users в БД

---

## Этап 2: Аутентификация и авторизация (Неделя 3-4)

### Теоретический материал

#### JWT токены
JWT (JSON Web Token) — это способ передачи данных между сторонами в компактном виде.

**Аналогия:** Как пропуск в спортзал
- При входе (логин) выдаётся пропуск (токен)
- Пропуск содержит информацию о владельце
- Пропуск имеет срок действия
- Охранник проверяет пропуск при каждом входе

#### Password hashing
Пароли никогда не хранятся в открытом виде! Используется хэширование.

**Инструменты:** `passlib` с алгоритмом bcrypt

---

### Задачи

#### 2.1 SQLAlchemy модель User
**Файл:** `app/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), default="manager")  # admin или manager
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    clients = relationship("Client", back_populates="creator")
    created_deals = relationship("Deal", foreign_keys="Deal.created_by", back_populates="creator")
    assigned_deals = relationship("Deal", foreign_keys="Deal.assigned_to", back_populates="assignee")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    interactions = relationship("Interaction", back_populates="user")
```

**Ожидаемый результат:** Модель User создана в коде

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Все поля соответствуют спецификации
- [ ] Настроены индексы для email и username

---

#### 2.2 Pydantic DTO для аутентификации
**Файл:** `app/dtos/auth.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreateDTO(BaseModel):
    """DTO для регистрации нового пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str | None = None

class UserLoginDTO(BaseModel):
    """DTO для входа в систему"""
    username: str
    password: str

class UserResponseDTO(BaseModel):
    """DTO для ответа с данными пользователя"""
    id: int
    username: str
    email: str
    full_name: str | None
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class TokenDTO(BaseModel):
    """DTO для ответа с токеном"""
    access_token: str
    token_type: str = "bearer"
```

**Ожидаемый результат:** Pydantic DTO готовы

---

#### 2.3 Сервис авторизации
**Файл:** `app/services/auth_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.dtos.auth import UserCreateDTO, UserLoginDTO
from app.utils.auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from app.config import settings
from typing import Optional

class AuthService:
    """Сервис для работы с аутентификацией"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, user_data: UserCreateDTO) -> User:
        """Регистрация нового пользователя"""
        # Проверка, что пользователь уже существует
        result = await self.db.execute(
            select(User).where(
                (User.username == user_data.username) | 
                (User.email == user_data.email)
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("Пользователь уже существует")
        
        # Создание нового пользователя
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def login(self, credentials: UserLoginDTO) -> dict:
        """Вход в систему"""
        result = await self.db.execute(
            select(User).where(User.username == credentials.username)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Неверные учетные данные")
        
        if not user.is_active:
            raise ValueError("Пользователь неактивен")
        
        # Создание токена
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
```

---

#### 2.4 Утилиты для работы с паролями и токенами
**Файл:** `app/utils/auth.py`

```python
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хэширование пароля"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """Расшифровка токена"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

**Ожидаемый результат:** Утилиты работают

**Критерии приёмки:**
- [ ] Функция `hash_password("secret")` возвращает хэш
- [ ] Функция `verify_password("secret", hashed)` возвращает True для верного пароля

---

#### 2.5 Зависимость для получения текущего пользователя
**Файл:** `app/deps/auth.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Проверяет токен и возвращает текущего пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    service = AuthService(db)
    user = await service.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user
```

**Ожидаемый результат:** Функция Depends работает

---

#### 2.6 Роутеры аутентификации
**Файл:** `app/routes/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dtos.auth import UserCreateDTO, UserLoginDTO, UserResponseDTO, TokenDTO
from app.services.auth_service import AuthService
from app.deps.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateDTO,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    service = AuthService(db)
    try:
        user = await service.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenDTO)
async def login(
    credentials: UserLoginDTO,
    db: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    service = AuthService(db)
    try:
        token_data = await service.login(credentials)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserResponseDTO)
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить данные текущего пользователя"""
    return current_user
```

**Ожидаемый результат:** Все эндпоинты работают

**Критерии приёмки:**
- [ ] POST /api/auth/register создаёт пользователя
- [ ] POST /api/auth/login возвращает токен
- [ ] GET /api/auth/me возвращает данные текущего пользователя
- [ ] Неавторизованные запросы возвращают 401

---

## Этап 3: Подключение роутеров в main.py

**Файл:** `app/main.py`

```python
from fastapi import FastAPI
from app.routes import auth, clients, deals, tasks, dashboard
from app.database import engine
from app.models import user  # Импорт для создания таблиц

app = FastAPI(title="CRM API", version="1.0.0")

# Подключение роутеров
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(deals.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "CRM API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## Этап 4: Интеграция и тестирование (Неделя 14-15)

### Задачи

#### 4.1 Координация бэкенд-команды
1. Проверить, что все CRUD операции работают
2. Проверить связи между моделями
3. Убедиться, что аутентификация работает везде

#### 4.2 Тестирование с фронтендом
**Взаимодействие с Дмитрием:**
1. Предоставить актуальную документацию API
2. Помогать с вопросами по интеграции
3. Тестировать совместную работу

#### 4.3 Деплой
**Взаимодействие с Николаем:**
1. Убедиться, что все миграции работают
2. Проверить переменные окружения для продакшена
3. Протестировать на production сервере

---

## Git Workflow

### Ветка
```
feature/auth-daniil
```

### Коммиты
```
feat: add project structure with DDD
feat: add database connection
feat: add User model
feat: add auth DTOs
feat: add auth service
feat: add authentication routes
```

### Перед слиянием в main
```bash
git fetch origin
git rebase origin/main
# Разрешить конфликты
git push origin feature/auth-daniil
# Создать Pull Request
```

---

## Критерии приёмки всего этапа

- [ ] Приложение запускается без ошибок
- [ ] DDD структура соблюдена
- [ ] Все эндпоинты аутентификации работают
- [ ] Пароли хэшируются и проверяются корректно
- [ ] JWT токены создаются и валидируются
- [ ] Защищённые роуты требуют токен
- [ ] Документация `/docs` работает
- [ ] Код проходит проверку линтером (flake8/black)
- [ ] Нет паролей и секретов в коде

---

## Взаимодействие с командой

### Ежедневные встречи (15 минут)
- Отчёт о прогрессе
- Блокирующие проблемы
- Планы на день

### Взаимодействие с Соней
- Помощь с настройкой SQLAlchemy
- Консультации по Pydantic DTO
- Проверка DDD структуры

### Взаимодействие с Эвелиной
- Помощь с настройкой SQLAlchemy
- Консультации по DTO для Deals

### Взаимодействие с Дмитрием
- Согласование формата API
- Предоставление тестовых данных

### Взаимодействие с Николаем
- Настройка Docker
- Деплой

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка окружения | Неделя 1-2 | |
| Аутентификация | Неделя 3-4 | |
| Интеграция | Неделя 14-15 | |

---

*Документ согласован с преподавателем (Team Lead)*
