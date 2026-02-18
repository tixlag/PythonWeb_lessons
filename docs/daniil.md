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
│   └── models/             # SQLAlchemy модели
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
**Взаимодействие с Никопаем (DevOps):** Попроси его предоставить готовый `docker-compose.yml` с PostgreSQL

**Задачи:**
1. Настроить подключение к PostgreSQL через SQLAlchemy
2. Создать файл `.env` с переменными окружения
3. Протестировать подключение к БД

**Пример аналогии (не решение):**
```python
# Представь, что подключаешься к библиотеке
# Нужно знать: адрес, имя читателя, пароль
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/crm"
```

**Подсказка:** Используй асинхронный движок `create_async_engine` для работы с FastAPI

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

**Структура JWT:**
```
header.payload.signature
```

#### Password hashing
Пароли никогда не хранятся в открытом виде! Используется хэширование.

**Аналогия:** Как сейф
- Пароль "123456" кладётся в сейф
- В сейф попадает только "зашифрованная" версия
- При проверке сравниваются "зашифрованные" версии
- Реальный пароль никогда не хранится

**Инструменты:** `passlib` с алгоритмом bcrypt

---

### Задачи

#### 2.1 Создание SQLAlchemy модели User
**Файл:** `app/models/user.py`

**Поля:**
- id (Integer, PK)
- username (String, unique, not null)
- email (String, unique, not null)
- hashed_password (String, not null)
- full_name (String, nullable)
- role (String, default="manager") — admin или manager
- is_active (Boolean, default=True)
- created_at (DateTime)
- updated_at (DateTime)

**Ожидаемый результат:** Модель User создана в коде

**Критерии приёмки:**
- [ ] Модель наследуется от Base
- [ ] Все поля соответствуют спецификации
- [ ] Настроены индексы для email и username

---

#### 2.2 Pydantic модели для аутентификации
**Файл:** `app/schemas/auth.py`

**Создай модели:**

```python
# Для регистрации — как анкета при устройстве на работу
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str | None = None

# Для входа — как заполнение пропуска
class UserLogin(BaseModel):
    username: str
    password: str

# Для ответа — что показываем о себе
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    role: str
    
    class Config:
        from_attributes = True
```

**Ожидаемый результат:** Pydantic схемы готовы

---

#### 2.3 Реализация хэширования паролей
**Файл:** `app/utils/auth.py`

**Инструменты:** `passlib[bcrypt]`, `python-jose`, `python-multipart`

```python
# Аналогия: Шифрование сейфа
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Превращает пароль в хэш"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет, совпадает ли пароль с хэшем"""
    return pwd_context.verify(plain, hashed)
```

**Ожидаемый результат:** Функции хэширования работают

**Критерии приёмки:**
- [ ] Функция `hash_password("secret")` возвращает хэш
- [ ] Функция `verify_password("secret", hashed)` возвращает True для верного пароля

---

#### 2.4 Создание JWT токенов
**Файл:** `app/utils/auth.py`

```python
# Аналогия: Изготовление пропуска
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "твой-секретный-ключ"  # В реальном проекте — из .env
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Создаёт JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Расшифровывает токен"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**Подсказка:** SECRET_KEY должен быть в `.env` и никогда не попадать в Git!

**Ожидаемый результат:** Токены создаются и валидируются

---

#### 2.5 Зависимость для получения текущего пользователя
**Файл:** `app/deps/auth.py`

```python
# Аналогия: Охранник на проходной
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Проверяет токен и возвращает пользователя"""
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
    
    # Здесь нужно получить пользователя из БД
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user
```

**Ожидаемый результат:** Функция Depends работает

---

#### 2.6 Роутеры аутентификации
**Файл:** `app/routers/auth.py`

**Эндпоинты:**

```python
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Регистрация нового пользователя"""
    # 1. Проверить, что пользователь уже существует
    # 2. Хэшировать пароль
    # 3. Создать пользователя в БД
    # 4. Вернуть данные пользователя

@router.post("/login")
async def login(credentials: UserLogin):
    """Вход в систему"""
    # 1. Найти пользователя по username
    # 2. Проверить пароль
    # 3. Создать JWT токен
    # 4. Вернуть токен

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить данные текущего пользователя"""
    return current_user
```

**Формат ответа при логине:**
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer"
}
```

**Ожидаемый результат:** Все эндпоинты работают

**Критерии приёмки:**
- [ ] POST /api/auth/register создаёт пользователя
- [ ] POST /api/auth/login возвращает токен
- [ ] GET /api/auth/me возвращает данные текущего пользователя
- [ ] Неавторизованные запросы возвращают 401

---

## Этап 3: Интеграция и тестирование (Неделя 14-15)

### Задачи

#### 3.1 Координация бэкенд-команды
1. Проверить, что все CRUD операции работают
2. Проверить связи между моделями
3. Убедиться, что аутентификация работает везде

#### 3.2 Тестирование с фронтендом
**Взаимодействие с Дмитрием:**
1. Предоставить актуальную документацию API
2. Помогать с вопросами по интеграции
3. Тестировать совместную работу

#### 3.3 Деплой
**Взаимодействие с Никопаем:**
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
feat: add project structure
feat: add database connection
feat: add User model
feat: add password hashing utilities
feat: add JWT token generation
feat: add authentication endpoints
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
- Консультации по Pydantic

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
