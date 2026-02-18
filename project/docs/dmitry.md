# Инструкция для Frontend Lead — Дмитрий

**Роль:** Frontend Lead  
**Зона ответственности:** Архитектура фронтенда, аутентификация, стилизация  
**Стек:** Vanilla JavaScript, HTML, CSS

---

## Общие обязанности

1. Координация работы фронтенд-команды (3 человека)
2. Настройка структуры проекта
3. Реализация аутентификации (Login/Register)
4. Управление токенами
5. Защищённые маршруты
6. Общие стили CSS
7. Взаимодействие с Backend Lead (Даниил)

---

## Теоретический материал

### Fetch API

Встроенный способ делать HTTP запросы в браузере.

**Пример:**
```javascript
// GET запрос
const response = await fetch('/api/data');
const data = await response.json();

// POST запрос
const response = await fetch('/api/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name: 'John' })
});
```

### LocalStorage

Хранение данных в браузере.

**Пример:**
```javascript
// Сохранить токен
localStorage.setItem('token', 'abc123');

// Получить токен
const token = localStorage.getItem('token');

// Удалить токен
localStorage.removeItem('token');
```

### Protected Routes (Защищённые маршруты)

Проверка авторизации перед показом страницы.

**Пример:**
```javascript
function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html';
    }
}
```

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Создание структуры проекта
```
frontend/
├── index.html              # Главная страница (редирект на /clients)
├── login.html              # Страница входа
├── register.html           # Страница регистрации
├── dashboard.html          # Дашборд
├── clients.html            # Страница клиентов
├── deals.html              # Страница сделок
├── tasks.html              # Страница задач
├── css/
│   └── style.css           # Общие стили
├── js/
│   ├── api.js              # API клиент
│   ├── auth.js             # Аутентификация
│   ├── router.js           # Маршрутизация
│   └── app.js              # Главный файл
└── assets/
    └── icons/
```

**Ожидаемый результат:** Структура проекта создана

---

#### 1.2 Настройка стилей
**Файл:** `css/style.css`

**Задачи:**
1. Создать CSS переменные для цветов
2. Настроить базовые стили (reset)
3. Создать сетку (grid/flexbox)
4. Типографика

```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --danger-color: #e74c3c;
    --dark-color: #2c3e50;
    --light-color: #ecf0f1;
    --border-radius: 8px;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--light-color);
    color: var(--dark-color);
}
```

**Ожидаемый результат:** Базовые стили готовы

---

## Этап 2: API клиент и аутентификация (Неделя 9-10)

### Задачи

#### 2.1 API клиент
**Файл:** `js/api.js`

```javascript
const API_URL = 'http://localhost:8000';

class ApiClient {
    constructor() {
        this.baseUrl = API_URL;
    }

    getToken() {
        return localStorage.getItem('token');
    }

    async request(endpoint, options = {}) {
        const token = this.getToken();
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login.html';
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка запроса');
        }

        if (response.status === 204) {
            return null;
        }

        return response.json();
    }

    // GET
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

const api = new ApiClient();
```

**Ожидаемый результат:** API клиент готов

---

#### 2.2 Модуль аутентификации
**Файл:** `js/auth.js`

```javascript
class Auth {
    constructor() {
        this.tokenKey = 'token';
        this.userKey = 'user';
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    getUser() {
        const user = localStorage.getItem(this.userKey);
        return user ? JSON.parse(user) : null;
    }

    setUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    logout() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
        window.location.href = '/login.html';
    }

    async login(username, password) {
        const response = await fetch(`${api.baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка входа');
        }

        const data = await response.json();
        this.setToken(data.access_token);
        
        // Получить данные пользователя
        await this.fetchCurrentUser();
        
        return data;
    }

    async register(userData) {
        const response = await fetch(`${api.baseUrl}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка регистрации');
        }

        return response.json();
    }

    async fetchCurrentUser() {
        const user = await api.get('/api/auth/me');
        this.setUser(user);
        return user;
    }
}

const auth = new Auth();
```

**Наводящий вопрос:** Как обрабатывать ошибки входа?
**Подсказка:** Показывай сообщение об ошибке пользователю

**Ожидаемый результат:** Аутентификация работает

---

#### 2.3 Страница входа
**Файл:** `login.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Вход — CRM</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <div class="auth-container">
        <form id="loginForm" class="auth-form">
            <h1>Вход в систему</h1>
            
            <div class="form-group">
                <label for="username">Имя пользователя</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div id="error" class="error-message"></div>
            
            <button type="submit">Войти</button>
            
            <p class="auth-link">
                Нет аккаунта? <a href="/register.html">Регистрация</a>
            </p>
        </form>
    </div>
    
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script>
        // Если уже авторизован — редирект
        if (auth.isAuthenticated()) {
            window.location.href = '/clients.html';
        }

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorEl = document.getElementById('error');
            
            try {
                await auth.login(username, password);
                window.location.href = '/clients.html';
            } catch (error) {
                errorEl.textContent = error.message;
            }
        });
    </script>
</body>
</html>
```

**Стили:**
```css
.auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.auth-form {
    background: white;
    padding: 2rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    width: 100%;
    max-width: 400px;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: var(--border-radius);
}

button[type="submit"] {
    width: 100%;
    padding: 0.75rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
}

.error-message {
    color: var(--danger-color);
    margin-bottom: 1rem;
}
```

**Ожидаемый результат:** Страница входа работает

**Критерии приёмки:**
- [ ] Форма входа отправляется
- [ ] Токен сохраняется в localStorage
- [ ] При ошибке показывается сообщение
- [ ] При успехе — редирект на clients.html
- [ ] Неавторизованные — редирект на login.html

---

#### 2.4 Страница регистрации
**Файл:** `register.html`

Аналогично login.html, но с дополнительными полями:
- email
- full_name

**Ожидаемый результат:** Регистрация работает

---

#### 2.5 Защищённые страницы
**Файл:** `js/app.js`

Добавь на каждую страницу проверку:
```javascript
if (!auth.isAuthenticated()) {
    window.location.href = '/login.html';
}
```

---

## Этап 3: Общие компоненты (Неделя 11-12)

### Задачи

#### 3.1 Header/Navigation
**Файл:** `js/components/header.js`

```javascript
function createHeader() {
    const user = auth.getUser();
    
    return `
        <header class="header">
            <div class="header-logo">CRM System</div>
            <nav class="header-nav">
                <a href="/clients.html">Клиенты</a>
                <a href="/deals.html">Сделки</a>
                <a href="/tasks.html">Задачи</a>
                <a href="/dashboard.html">Дашборд</a>
            </nav>
            <div class="header-user">
                <span>${user?.username || 'Пользователь'}</span>
                <button id="logoutBtn">Выход</button>
            </div>
        </header>
    `;
}

// Обработчик выхода
document.getElementById('logoutBtn').addEventListener('click', () => {
    auth.logout();
});
```

**Ожидаемый результат:** Header готов

---

#### 3.2 Modal (всплывающее окно)
**Файл:** `js/components/modal.js`

```javascript
function showModal(title, content, onConfirm = null) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${title}</h2>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">${content}</div>
            ${onConfirm ? `
                <div class="modal-footer">
                    <button class="btn-cancel">Отмена</button>
                    <button class="btn-confirm">Подтвердить</button>
                </div>
            ` : ''}
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Закрытие
    modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    modal.querySelector('.btn-cancel')?.addEventListener('click', () => modal.remove());
    
    return modal;
}
```

**Ожидаемый результат:** Modal компонент готов

---

## Этап 4: Координация команды (Неделя 14-15)

### Задачи

#### 4.1 Проверка работы Ивана
- Страницы клиентов работают
- Формы создания/редактирования работают

#### 4.2 Проверка работы Александра
- Страницы сделок работают
- Kanban доска работает
- Задачи работают

#### 4.3 Интеграция с бэкендом
**Взаимодействие с Даниилом:**
- Тестирование всех API вызовов
- Исправление CORS проблем
- Тестирование на production

---

## Git Workflow

### Ветка
```
feature/frontend-structure-dmitry
```

### Коммиты
```
feat: add project structure
feat: add base styles
feat: add API client
feat: add authentication module
feat: add login page
feat: add register page
feat: add header component
feat: add modal component
```

---

## Взаимодействие с командой

### С Иваном (Frontend)
- Координация работы
- Помощь с API
- Проверка качества кода

### С Александром (Frontend)
- Координация работы
- Проверка качества кода

### С Даниилом (Backend Lead)
- Согласование формата API
- Тестирование интеграции

---

## Критерии приёмки

- [ ] Структура проекта создана
- [ ] Стили настроены
- [ ] API клиент работает
- [ ] Страница входа работает
- [ ] Страница регистрации работает
- [ ] Токены сохраняются правильно
- [ ] Protected routes работают
- [ ] Header/Navigation готов
- [ ] Modal компонент готов

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| API и Auth | Неделя 9-10 | |
| Компоненты | Неделя 11-12 | |
| Координация | Неделя 14-15 | |

---

*При вопросах обращаться к преподавателю (Team Lead)*
