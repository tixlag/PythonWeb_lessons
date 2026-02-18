# Домашнее задание: Docker + Flask + Frontend

## Цель задания

Изучить работу с Docker, Docker Compose и создать полноценное веб-приложение с разделением на фронтенд и бэкенд.

## Описание проекта

Вам предоставлена готовая Docker-инфраструктура для веб-приложения по управлению пользователями. Проект состоит из:

- **Backend** - Flask приложение с REST API
- **Frontend** - Статический HTML с vanilla JavaScript
- **Nginx Gateway** - Маршрутизатор запросов

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    nginx-gateway                        │
│              (Порт 5000 на хосте)                       │
├─────────────────────────────────────────────────────────┤
│  localhost:5000      →  frontend (Nginx)               │
│  api.localhost:5000  →  backend (Flask)                │
└─────────────────────────────────────────────────────────┘
```

## Задание

### Часть 1: Запуск проекта

1. **Настройка hosts файла**

   Для корректной работы маршрутизации необходимо добавить запись `api.localhost` в файл hosts вашей операционной системы.

   **Linux/macOS:**
   ```bash
   sudo echo "127.0.0.1 api.localhost" >> /etc/hosts
   ```

   **Windows:**
   1. Откройте Блокнот от имени администратора
   2. Откройте файл `C:\Windows\System32\drivers\etc\hosts`
   3. Добавьте строку: `127.0.0.1 api.localhost`
   4. Сохраните файл

2. **Запуск контейнеров**

   Перейдите в директорию `lesson_6` и выполните команду:

   ```bash
   docker-compose up --build
   ```

   Эта команда:
   - Соберёт Docker-образы для всех сервисов
   - Запустит три контейнера: backend, frontend, nginx-gateway
   - Настроит сеть для взаимодействия между контейнерами

3. **Проверка работы**

   Откройте в браузере:
   - **Frontend**: http://localhost:5000
   - **Backend API**: http://api.localhost:5000/health

   Вы должны увидеть:
   - На фронтенде - интерфейс для управления пользователями
   - На API - JSON ответ со статусом здоровья сервера

### Часть 2: Изучение проекта

1. **Изучите структуру проекта**

   ```
   lesson_6/
   ├── backend/
   │   ├── Dockerfile          # Конфигурация контейнера бэкенда
   │   ├── server.py           # Flask приложение
   │   ├── utils.py            # Вспомогательные функции
   │   └── requirements.txt    # Зависимости Python
   ├── frontend/
   │   ├── Dockerfile          # Конфигурация контейнера фронтенда
   │   └── index.html          # Frontend приложение
   ├── nginx/
   │   ├── Dockerfile          # Конфигурация контейнера nginx
   │   └── nginx.conf          # Конфигурация маршрутизации
   └── docker-compose.yml      # Оркестрация сервисов
   ```

2. **Изучите API эндпоинты**

   Бэкенд предоставляет следующие эндпоинты:
   - `GET /users` - Получить всех пользователей
   - `GET /users/<id>` - Получить пользователя по ID
   - `POST /users` - Создать нового пользователя
   - `PUT /users/<id>` - Обновить пользователя
   - `DELETE /users/<id>` - Удалить пользователя
   - `GET /health` - Проверка работоспособности

3. **Протестируйте API**

   Используйте curl или Postman для тестирования:

   ```bash
   # Создать пользователя
   curl -X POST http://api.localhost:5000/users \
     -H "Content-Type: application/json" \
     -d '{"name":"Иван","email":"ivan@example.com"}'

   # Получить всех пользователей
   curl http://api.localhost:5000/users

   # Обновить пользователя
   curl -X PUT http://api.localhost:5000/users/1 \
     -H "Content-Type: application/json" \
     -d '{"name":"Иван Иванов"}'

   # Удалить пользователя
   curl -X DELETE http://api.localhost:5000/users/1
   ```

### Часть 3: Добавление функционала редактирования

**Внимание:** Функционал редактирования уже реализован в файле `frontend/index.html`. Ваша задача - изучить его реализацию и понять, как он работает.

#### Что нужно изучить:

1. **Модальное окно редактирования**

   Найдите в HTML секцию с `id="editModal"` - это модальное окно для редактирования пользователя.

2. **Стили для модального окна**

   В CSS найдите классы:
   - `.modal` - базовый стиль модального окна
   - `.modal.show` - класс для отображения окна
   - `.modal-content` - контент модального окна
   - `.modal-header` - заголовок модального окна
   - `.modal-actions` - кнопки действий

3. **JavaScript функции**

   Создайте следующие функции в JavaScript:

   - `openEditModal(userId, name, email)` - открывает модальное окно с данными пользователя
   - `closeEditModal()` - закрывает модальное окно
   - `updateUser(userId, name, email)` - отправляет PUT запрос на сервер для обновления
   - `showEditMessage(message, type)` - отображает сообщения об успехе/ошибке

4. **Кнопка редактирования**

   В функции `renderUsers()` создайте кнопку редактирования:
   ```javascript
   <button class="btn-small btn-edit" onclick="openEditModal(${user.id}, '${escapeHtml(user.name)}', '${escapeHtml(user.email)}')">Редактировать</button>
   ```

5. **Обработчик формы редактирования**

   Создайте обработчик отправки формы редактирования:
   ```javascript
   editForm.addEventListener('submit', (e) => {
       e.preventDefault();
       const userId = document.getElementById('editUserId').value;
       const name = document.getElementById('editName').value.trim();
       const email = document.getElementById('editEmail').value.trim();
       
       if (name && email) {
           updateUser(userId, name, email);
       }
   });
   ```

#### Как это работает:

1. Пользователь нажимает кнопку "Редактировать" рядом с пользователем
2. Функция `openEditModal()` заполняет поля формы текущими данными и показывает модальное окно
3. Пользователь изменяет данные и нажимает "Сохранить"
4. Форма отправляется, вызывается `updateUser()`
5. Отправляется PUT запрос на `http://api.localhost:5000/users/{id}`
6. При успешном ответе модальное окно закрывается и список пользователей обновляется

### Часть 4: Дополнительные задания (по желанию)

1. **Добавьте валидацию email на фронтенде**

   Проверьте формат email перед отправкой на сервер.

2. **Добавьте сортировку пользователей**

   Добавьте возможность сортировки по имени или email.

3. **Добавьте поиск пользователей**

   Реализуйте поле поиска для фильтрации списка пользователей.

4. **Добавьте пагинацию**

   Если пользователей станет много, реализуйте постраничную навигацию.

5. **Добавьте подтверждение удаления**

   Уже реализовано через `confirm()`, но можно сделать красивое модальное окно.

## Полезные команды

```bash
# Запуск контейнеров
docker compose up --build

# Запуск в фоновом режиме
docker compose up -d

# Остановка контейнеров
docker compose down

# Просмотр логов
docker compose logs

# Логи конкретного сервиса
docker compose logs backend
docker compose logs frontend
docker compose logs nginx-gateway

# Пересборка образа
docker compose build

# Перезапуск сервиса
docker compose restart backend
```

## Требования к выполнению

- [x] Проект успешно запущен через Docker Compose
- [x] Frontend доступен по адресу http://localhost:5000
- [x] Backend API доступен по адресу http://api.localhost:5000
- [x] Можно создавать новых пользователей
- [x] Можно просматривать список пользователей
- [x] Можно редактировать существующих пользователей
- [x] Можно удалять пользователей
- [x] Понятна архитектура проекта и взаимодействие компонентов

## Вопросы для самопроверки

1. Зачем нужен nginx-gateway?
2. Как работает маршрутизация запросов между frontend и backend?
3. Что такое Docker Compose и зачем он нужен?
4. Как frontend общается с backend?
5. Зачем нужно добавлять api.localhost в hosts файл?
6. Как работает hot-reload для бэкенда?
7. Какие HTTP методы используются в CRUD операциях?

## Сдача задания

Для сдачи задания:
1. Сделайте скриншот работающего приложения
2. Продемонстрируйте все функции (создание, редактирование, удаление)
3. Будьте готовы ответить на вопросы по архитектуре проекта

## Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MDN Web Docs - Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [Nginx Documentation](https://nginx.org/en/docs/)
