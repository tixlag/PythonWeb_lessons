# Инструкция для Frontend Developer — Иван

**Роль:** Frontend Developer  
**Зона ответственности:** Клиенты (Clients)  
**Стек:** Vanilla JavaScript, HTML, CSS

---

## Общие обязанности

1. Реализация страницы списка клиентов
2. Форма создания/редактирования клиента
3. Поиск и фильтрация клиентов
4. Просмотр карточки клиента
5. Взаимодействие с Backend (Соня) и Frontend Lead (Дмитрий)

---

## Теоретический материал

### Работа с DOM

DOM (Document Object Model) — представление HTML в JavaScript.

**Пример:**
```javascript
// Создать элемент
const div = document.createElement('div');
div.className = 'card';
div.textContent = 'Привет';

// Добавить в DOM
document.body.appendChild(div);

// Найти элемент
const element = document.querySelector('#myId');
const elements = document.querySelectorAll('.myClass');

// Изменить содержимое
element.innerHTML = '<strong>Новый</strong> контент';
```

### Обработка форм

**Пример:**
```javascript
form.addEventListener('submit', (e) => {
    e.preventDefault(); // Отменить стандартную отправку
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    console.log(data);
});
```

### Шаблонизация

**Пример:**
```javascript
function renderClient(client) {
    return `
        <div class="client-card">
            <h3>${client.name}</h3>
            <p>${client.email}</p>
            <p>${client.phone}</p>
        </div>
    `;
}

// Использование
const clients = [{name: 'Иван', email: 'ivan@test.com'}, ...];
const html = clients.map(renderClient).join('');
document.getElementById('list').innerHTML = html;
```

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Настройка рабочего окружения
**Инструменты:** Git, редактор кода

**Задачи:**
1. Клонировать репозиторий
2. Создать ветку: `git checkout -b feature/frontend-clients-ivan`
3. Проверить структуру проекта (спросить у Дмитрия)

**Ожидаемый результат:** Проект готов к работе

---

#### 1.2 Изучение API
**Инструменты:** Документация

**Изучить у Сони:**
- Какие эндпоинты есть для клиентов
- Какие поля принимает/возвращает API
- Как работает пагинация

**Ожидаемый результат:** Понимание API

---

## Этап 2: Страница клиентов (Неделя 11-12)

### Задачи

#### 2.1 HTML страницы
**Файл:** `clients.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Клиенты — CRM</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <!-- Header будет добавлен Дмитрием -->
    <div id="header"></div>
    
    <main class="main-content">
        <div class="page-header">
            <h1>Клиенты</h1>
            <button id="addClientBtn" class="btn-primary">Добавить клиента</button>
        </div>
        
        <!-- Поиск -->
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Поиск по имени или email...">
            <button id="searchBtn" class="btn-secondary">Найти</button>
        </div>
        
        <!-- Список клиентов -->
        <div id="clientsList" class="clients-grid">
            <!-- Клиенты будут загружены здесь -->
        </div>
        
        <!-- Пагинация -->
        <div class="pagination" id="pagination">
            <!-- Кнопки пагинации -->
        </div>
    </main>
    
    <!-- Модальное окно (подключить компонент от Дмитрия) -->
    <div id="modalContainer"></div>
    
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/clients.js"></script>
</body>
</html>
```

**Ожидаемый результат:** HTML готов

---

#### 2.2 JavaScript логика
**Файл:** `js/clients.js`

```javascript
// Проверка авторизации
if (!auth.isAuthenticated()) {
    window.location.href = '/login.html';
}

// Состояние
let currentPage = 1;
let searchQuery = '';

// Загрузка клиентов
async function loadClients() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: 10,
            ...(searchQuery && { search: searchQuery })
        });
        
        const data = await api.get(`/api/clients/?${params}`);
        renderClients(data.items);
        renderPagination(data);
    } catch (error) {
        console.error('Ошибка загрузки клиентов:', error);
        showError('Не удалось загрузить клиентов');
    }
}

// Отображение списка
function renderClients(clients) {
    const container = document.getElementById('clientsList');
    
    if (clients.length === 0) {
        container.innerHTML = '<p class="empty">Клиентов не найдено</p>';
        return;
    }
    
    container.innerHTML = clients.map(client => `
        <div class="client-card" data-id="${client.id}">
            <h3>${escapeHtml(client.name)}</h3>
            <p class="client-email">${escapeHtml(client.email || '—')}</p>
            <p class="client-phone">${escapeHtml(client.phone || '—')}</p>
            <p class="client-company">${escapeHtml(client.company_name || '—')}</p>
            <div class="client-actions">
                <button class="btn-edit" data-id="${client.id}">Редактировать</button>
                <button class="btn-delete" data-id="${client.id}">Удалить</button>
            </div>
        </div>
    `).join('');
    
    // Добавить обработчики
    container.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', () => openEditModal(btn.dataset.id));
    });
    
    container.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', () => deleteClient(btn.dataset.id));
    });
}

// Экранирование HTML (безопасность)
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

**Ожидаемый результат:** Загрузка и отображение работают

**Критерии приёмки:**
- [ ] Клиенты загружаются с API
- [ ] Клиенты отображаются на странице

---

#### 2.3 Поиск
```javascript
// Поиск
document.getElementById('searchBtn').addEventListener('click', () => {
    searchQuery = document.getElementById('searchInput').value;
    currentPage = 1;
    loadClients();
});

// Поиск по Enter
document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchQuery = e.target.value;
        currentPage = 1;
        loadClients();
    }
});
```

**Ожидаемый результат:** Поиск работает

---

#### 2.4 Пагинация
```javascript
function renderPagination(data) {
    const container = document.getElementById('pagination');
    const totalPages = Math.ceil(data.total / data.page_size);
    
    let html = '';
    
    if (currentPage > 1) {
        html += `<button class="btn-page" data-page="${currentPage - 1}">Предыдущая</button>`;
    }
    
    html += `<span>Страница ${currentPage} из ${totalPages}</span>`;
    
    if (currentPage < totalPages) {
        html += `<button class="btn-page" data-page="${currentPage + 1}">Следующая</button>`;
    }
    
    container.innerHTML = html;
    
    container.querySelectorAll('.btn-page').forEach(btn => {
        btn.addEventListener('click', () => {
            currentPage = parseInt(btn.dataset.page);
            loadClients();
        });
    });
}
```

**Ожидаемый результат:** Пагинация работает

---

## Этап 3: Формы (Неделя 13)

### Задачи

#### 3.1 Модальное окно создания
```javascript
function openCreateModal() {
    const modal = document.getElementById('modalContainer');
    
    modal.innerHTML = `
        <div class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Добавить клиента</h2>
                    <button class="modal-close">&times;</button>
                </div>
                <form id="clientForm">
                    <div class="form-group">
                        <label>Название *</label>
                        <input type="text" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email">
                    </div>
                    <div class="form-group">
                        <label>Телефон</label>
                        <input type="tel" name="phone">
                    </div>
                    <div class="form-group">
                        <label>Компания</label>
                        <input type="text" name="company_name">
                    </div>
                    <div class="form-group">
                        <label>Адрес</label>
                        <input type="text" name="address">
                    </div>
                    <div class="form-group">
                        <label>Заметки</label>
                        <textarea name="notes"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-cancel">Отмена</button>
                        <button type="submit" class="btn-primary">Создать</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // Обработчики закрытия
    modal.querySelector('.modal-close').addEventListener('click', closeModal);
    modal.querySelector('.btn-cancel').addEventListener('click', closeModal);
    modal.querySelector('.modal').addEventListener('click', (e) => {
        if (e.target === modal.querySelector('.modal')) closeModal();
    });
    
    // Отправка формы
    modal.querySelector('#clientForm').addEventListener('submit', handleCreate);
}

function closeModal() {
    document.getElementById('modalContainer').innerHTML = '';
}

async function handleCreate(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
        await api.post('/api/clients/', data);
        closeModal();
        loadClients();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}
```

**Ожидаемый результат:** Создание работает

---

#### 3.2 Модальное окно редактирования
```javascript
async function openEditModal(clientId) {
    try {
        const client = await api.get(`/api/clients/${clientId}`);
        
        const modal = document.getElementById('modalContainer');
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Редактировать клиента</h2>
                        <button class="modal-close">&times;</button>
                    </div>
                    <form id="editClientForm">
                        <input type="hidden" name="id" value="${client.id}">
                        <div class="form-group">
                            <label>Название *</label>
                            <input type="text" name="name" value="${escapeHtml(client.name)}" required>
                        </div>
                        <!-- Остальные поля -->
                        <div class="modal-footer">
                            <button type="button" class="btn-cancel">Отмена</button>
                            <button type="submit" class="btn-primary">Сохранить</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        modal.querySelector('#editClientForm').addEventListener('submit', handleEdit);
        // ... обработчики закрытия
        
    } catch (error) {
        alert('Ошибка загрузки клиента');
    }
}

async function handleEdit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    const id = data.id;
    delete data.id;
    
    try {
        await api.put(`/api/clients/${id}`, data);
        closeModal();
        loadClients();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}
```

**Ожидаемый результат:** Редактирование работает

---

#### 3.3 Удаление
```javascript
async function deleteClient(clientId) {
    if (!confirm('Вы уверены, что хотите удалить этого клиента?')) {
        return;
    }
    
    try {
        await api.delete(`/api/clients/${clientId}`);
        loadClients();
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
}
```

**Ожидаемый результат:** Удаление работает

---

## Этап 4: Интеграция (Неделя 14-15)

### Задачи

#### 4.1 Тестирование
- Все CRUD операции работают
- Поиск работает
- Пагинация работает

#### 4.2 Исправление багов
- Работа с Дмитрием и Соней

---

## Git Workflow

### Ветка
```
feature/frontend-clients-ivan
```

### Коммиты
```
feat: add clients page HTML
feat: add clients list rendering
feat: add search functionality
feat: add pagination
feat: add create client modal
feat: add edit client modal
feat: add delete client
```

---

## Взаимодействие с командой

### С Дмитрием (Frontend Lead)
- Получение компонентов (header, modal)
- Помощь с API клиентом
- Проверка качества кода

### С Соней (Backend)
- Получение документации по API
- Тестирование совместной работы
- Исправление ошибок

---

## Критерии приёмки

- [ ] Страница клиентов загружается
- [ ] Список клиентов отображается
- [ ] Поиск работает
- [ ] Пагинация работает
- [ ] Создание клиента работает
- [ ] Редактирование клиента работает
- [ ] Удаление клиента работает
- [ ] Сообщения об ошибках показываются

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Страница клиентов | Неделя 11-12 | |
| Формы | Неделя 13 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Дмитрию (Frontend Lead)*
