# Инструкция для DevOps Engineer — Николай

**Роль:** DevOps Engineer  
**Зона ответственности:** Инфраструктура, Docker, CI/CD, деплой  
**Стек:** Docker, Docker Compose, Nginx, GitHub Actions

---

## Общие обязанности

1. Настройка Docker Compose для всего приложения
2. Конфигурация Nginx
3. Скрипты для миграций
4. Настройка CI/CD
5. Деплой и мониторинг
6. Взаимодействие с Backend (Даниил) и Frontend (Дмитрий)

---

## Теоретический материал

### Docker

Контейнеризация приложений.

**Аналогия:** Как контейнер для перевозки грузов — всё упаковано и готово к отправке.

**Основные команды:**
```bash
docker build -t my-app .          # Собрать образ
docker run -p 8080:80 my-app      # Запустить контейнер
docker ps                         # Список работающих
docker logs -f container          # Логи
docker exec -it container bash   # Войти в контейнер
```

### Docker Compose

Запуск нескольких контейнеров вместе.

**Аналогия:** Как дирижёр оркестра — управляет всеми инструментами.

**Основные команды:**
```bash
docker-compose up -d              # Запустить все сервисы
docker-compose down                # Остановить
docker-compose logs -f             # Логи всех сервисов
docker-compose restart service    # Перезапустить сервис
```

### Nginx

Веб-сервер и обратный прокси.

**Аналогия:** Как ресепшен в отеле — принимает запросы и перенаправляет к нужному исполнителю.

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Создание структуры Docker
```
docker/
├── backend/
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

**Ожидаемый результат:** Структура создана

---

## Этап 2: Docker Compose (Неделя 3-4)

### Задачи

#### 2.1 Docker Compose файл
**Файл:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL база данных
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: crm_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: crm_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U crm_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://crm_user:${DB_PASSWORD}@postgres:5432/crm_db
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend (статика)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - ./frontend:/usr/share/nginx/html

  # Nginx
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

**Ожидаемый результат:** Docker Compose работает

**Критерии приёмки:**
- [ ] Все сервисы запускаются
- [ ] Backend доступен через nginx
- [ ] Frontend доступен через nginx

---

#### 2.2 Backend Dockerfile
**Файл:** `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**requirements.txt:**
```
fastapi
uvicorn[standard]
sqlalchemy
asyncpg
alembic
pydantic
pydantic[email]
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

---

#### 2.3 Frontend Dockerfile
**Файл:** `frontend/Dockerfile`

```dockerfile
FROM nginx:alpine

# Копирование статики
COPY . /usr/share/nginx/html/

# Копирование конфига nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## Этап 3: Nginx конфигурация (Неделя 5-6)

### Задачи

#### 3.1 Nginx конфиг
**Файл:** `nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Swagger UI
    location /docs {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    # OpenAPI JSON
    location /openapi.json {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
```

**Ожидаемый результат:** Nginx настроен

---

## Этап 4: Миграции и скрипты (Неделя 7-8)

### Задачи

#### 4.1 Скрипт миграций
**Файл:** `scripts/migrate.sh`

```bash
#!/bin/bash
set -e

echo "Waiting for database..."
sleep 5

echo "Running migrations..."
docker-compose exec -T backend alembic upgrade head

echo "Seeding initial data..."
docker-compose exec -T backend python -c "
from app.database import async_session
from app.models.user import User
from app.utils.auth import hash_password
import asyncio

async def seed():
    async with async_session() as session:
        # Создание админа
        admin = User(
            username='admin',
            email='admin@crm.local',
            hashed_password=hash_password('admin123'),
            full_name='Администратор',
            role='admin'
        )
        session.add(admin)
        await session.commit()

asyncio.run(seed())
"

echo "Done!"
```

**Ожидаемый результат:** Скрипт миграций работает

---

## Этап 5: CI/CD (Неделя 9-10)

### Задачи

#### 5.1 GitHub Actions workflow
**Файл:** `.github/workflows/ci.yml`

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run linter
        run: |
          pip install flake8 black
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          black --check .
      
      - name: Run tests
        run: |
          cd backend
          pytest

  build-docker:
    runs-on: ubuntu-latest
    needs: test-backend
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker-compose build
      
      - name: Run containers
        run: docker-compose up -d
      
      - name: Check services
        run: |
          sleep 10
          curl -f http://localhost/ || exit 1
          curl -f http://localhost/api/clients/ || exit 1

  deploy:
    runs-on: ubuntu-latest
    needs: build-docker
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to server
        run: |
          echo "Deploy commands here"
```

**Ожидаемый результат:** CI/CD настроен

---

## Этап 6: Production (Неделя 14-16)

### Задачи

#### 6.1 Production Dockerfile
**Файл:** `backend/Dockerfile.prod`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Не использовать --reload в продакшене!
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

#### 6.2 Production docker-compose
**Файл:** `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    # ... настройки для продакшена
    restart: always

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: always

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    restart: always
```

---

#### 6.3 Мониторинг (опционально)
```yaml
# Добавить в docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

---

## Git Workflow

### Ветка
```
infrastructure-docker-nikolai
```

### Коммиты
```
chore: add docker-compose.yml
chore: add backend Dockerfile
chore: add frontend Dockerfile
chore: configure nginx
chore: add migration script
ci: add GitHub Actions workflow
chore: add production Dockerfiles
```

---

## Взаимодействие с командой

### С Даниилом (Backend Lead)
- Настройка переменных окружения
- Проверка миграций
- Тестирование бэкенда в Docker

### С Дмитрием (Frontend Lead)
- Тестирование фронтенда в Docker
- Настройка Nginx для SPA

### С преподавателем (Lead DevOps)
- Деплой на сервер
- Мониторинг

---

## Критерии приёмки

- [ ] Docker Compose запускается
- [ ] Все сервисы работают
- [ ] Nginx проксирует на backend и frontend
- [ ] Миграции запускаются автоматически
- [ ] CI/CD работает
- [ ] Production сборка работает

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Docker Compose | Неделя 3-4 | |
| Nginx | Неделя 5-6 | |
| Миграции | Неделя 7-8 | |
| CI/CD | Неделя 9-10 | |
| Production | Неделя 14-16 | |

---

*При вопросах обращаться к преподавателю (Lead DevOps)*
