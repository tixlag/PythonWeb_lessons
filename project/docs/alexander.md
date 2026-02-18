# Инструкция для Frontend Developer — Александр

**Роль:** Frontend Developer  
**Зона ответственности:** Сделки (Deals), Задачи (Tasks), Дашборд  
**Стек:** Vanilla JavaScript, HTML, CSS

---

## Общие обязанности

1. Реализация Kanban доски для сделок
2. Страница задач
3. Дашборд со статистикой
4. Модальные окна
5. Взаимодействие с Backend (Эвелина, Павел) и Frontend Lead (Дмитрий)

---

## Теоретический материал

### Drag and Drop (Перетаскивание)

**Аналогия:** Как в Trello — перетаскивать карточки между колонками.

**Пример:**
```javascript
// Сделать элемент перетаскиваемым
element.draggable = true;

element.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', e.target.id);
});

element.addEventListener('dragover', (e) => {
    e.preventDefault(); // Разрешить drop
});

element.addEventListener('drop', (e) => {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    // Обработка drop
});
```

### Kanban доска

Доска с колонками, где каждая колонка — это статус.

**Аналогия:**
```
Новые     | Переговоры | Выиграны | Проиграны
--------------------------------------------------
Сделка 1  | Сделка 3   | Сделка 5 | Сделка 7
Сделка 2  | Сделка 4   |          |
```

---

## Этап 1: Подготовка (Неделя 1-2)

### Задачи

#### 1.1 Настройка рабочего окружения
**Инструменты:** Git, редактор кода

**Задачи:**
1. Клонировать репозиторий
2. Создать ветку: `git checkout -b feature/frontend-deals-alexander`
3. Проверить структуру проекта

---

## Этап 2: Kanban доска сделок (Неделя 13)

### Задачи

#### 2.1 HTML структура
**Файл:** `deals.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Сделки — CRM</title>
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/kanban.css">
</head>
<body>
    <div id="header"></div>
    
    <main class="main-content">
        <div class="page-header">
            <h1>Сделки</h1>
            <button id="addDealBtn" class="btn-primary">Добавить сделку</button>
        </div>
        
        <div class="kanban-board">
            <div class="kanban-column" data-status="new">
                <div class="column-header">
                    <h3>Новые</h3>
                    <span class="deal-count">0</span>
                </div>
                <div class="column-content" data-status="new">
                    <!-- Сделки -->
                </div>
            </div>
            
            <div class="kanban-column" data-status="negotiation">
                <div class="column-header">
                    <h3>Переговоры</h3>
                    <span class="deal-count">0</span>
                </div>
                <div class="column-content" data-status="negotiation">
                    <!-- Сделки -->
                </div>
            </div>
            
            <div class="kanban-column" data-status="won">
                <div class="column-header">
                    <h3>Выиграны</h3>
                    <span class="deal-count">0</span>
                </div>
                <div class="column-content" data-status="won">
                    <!-- Сделки -->
                </div>
            </div>
            
            <div class="kanban-column" data-status="lost">
                <div class="column-header">
                    <h3>Проиграны</h3>
                    <span class="deal-count">0</span>
                </div>
                <div class="column-content" data-status="lost">
                    <!-- Сделки -->
                </div>
            </div>
        </div>
    </main>
    
    <div id="modalContainer"></div>
    
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/deals.js"></script>
</body>
</html>
```

---

#### 2.2 Стили Kanban
**Файл:** `css/kanban.css`

```css
.kanban-board {
    display: flex;
    gap: 1rem;
    overflow-x: auto;
    padding: 1rem 0;
    min-height: calc(100vh - 200px);
}

.kanban-column {
    flex: 0 0 300px;
    background: #f5f5f5;
    border-radius: var(--border-radius);
    display: flex;
    flex-direction: column;
}

.column-header {
    padding: 1rem;
    background: var(--primary-color);
    color: white;
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.column-content {
    flex: 1;
    padding: 0.5rem;
    min-height: 200px;
}

.deal-card {
    background: white;
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    cursor: grab;
    transition: transform 0.2s, box-shadow 0.2s;
}

.deal-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.deal-card.dragging {
    opacity: 0.5;
}

.deal-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.deal-amount {
    color: var(--secondary-color);
    font-weight: 600;
}

.deal-client {
    color: #666;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

/* Цвета для разных статусов */
.kanban-column[data-status="new"] .column-header { background: #3498db; }
.kanban-column[data-status="negotiation"] .column-header { background: #f39c12; }
.kanban-column[data-status="won"] .column-header { background: #27ae60; }
.kanban-column[data-status="lost"] .column-header { background: #e74c3c; }
```

---

#### 2.3 JavaScript логика
**Файл:** `js/deals.js`

```javascript
if (!auth.isAuthenticated()) {
    window.location.href = '/login.html';
}

const STATUSES = ['new', 'negotiation', 'won', 'lost'];

// Загрузка сделок
async function loadDeals() {
    try {
        const data = await api.get('/api/deals/');
        renderDeals(data);
    } catch (error) {
        console.error('Ошибка загрузки сделок:', error);
    }
}

// Отображение сделок по колонкам
function renderDeals(deals) {
    // Очистить все колонки
    document.querySelectorAll('.column-content').forEach(col => {
        col.innerHTML = '';
    });
    
    // Счётчики
    const counts = { new: 0, negotiation: 0, won: 0, lost: 0 };
    
    deals.forEach(deal => {
        const card = createDealCard(deal);
        const column = document.querySelector(`.column-content[data-status="${deal.status}"]`);
        if (column) {
            column.appendChild(card);
            counts[deal.status]++;
        }
    });
    
    // Обновить счётчики
    STATUSES.forEach(status => {
        const countEl = document.querySelector(`.kanban-column[data-status="${status}"] .deal-count`);
        if (countEl) countEl.textContent = counts[status];
    });
}

// Создание карточки сделки
function createDealCard(deal) {
    const card = document.createElement('div');
    card.className = 'deal-card';
    card.draggable = true;
    card.dataset.id = deal.id;
    card.dataset.status = deal.status;
    
    card.innerHTML = `
        <div class="deal-title">${escapeHtml(deal.title)}</div>
        <div class="deal-amount">${formatMoney(deal.amount)}</div>
        <div class="deal-client">${escapeHtml(deal.client?.name || '—')}</div>
    `;
    
    // Drag events
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
    
    return card;
}

function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.id);
    e.target.classList.add('dragging');
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

// Настройка drop зон
document.querySelectorAll('.column-content').forEach(column => {
    column.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    
    column.addEventListener('drop', async (e) => {
        e.preventDefault();
        const dealId = e.dataTransfer.getData('text/plain');
        const newStatus = column.dataset.status;
        
        await updateDealStatus(dealId, newStatus);
    });
});

// Обновление статуса
async function updateDealStatus(dealId, newStatus) {
    try {
        await api.put(`/api/deals/${dealId}`, { status: newStatus });
        loadDeals();
    } catch (error) {
        alert('Ошибка обновления статуса: ' + error.message);
    }
}

// Форматирование денег
function formatMoney(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    }).format(amount);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Инициализация
loadDeals();
```

**Наводящий вопрос:** Как сделать так, чтобы при перетаскивании сделка не пропадала, если drop отменён?
**Подсказка:** Добавь проверку в drop handler

**Ожидаемый результат:** Kanban доска работает

---

## Этап 3: Страница задач (Неделя 13-14)

### Задачи

#### 3.1 HTML страницы
**Файл:** `tasks.html`

```html
<main class="main-content">
    <div class="page-header">
        <h1>Задачи</h1>
        <button id="addTaskBtn" class="btn-primary">Добавить задачу</button>
    </div>
    
    <!-- Фильтры -->
    <div class="filters">
        <select id="statusFilter">
            <option value="">Все статусы</option>
            <option value="todo">К выполнению</option>
            <option value="in_progress">В процессе</option>
            <option value="done">Выполнено</option>
        </select>
        
        <select id="priorityFilter">
            <option value="">Все приоритеты</option>
            <option value="high">Высокий</option>
            <option value="medium">Средний</option>
            <option value="low">Низкий</option>
        </select>
    </div>
    
    <!-- Список задач -->
    <div id="tasksList" class="tasks-list"></div>
</main>
```

---

#### 3.2 JavaScript задач
**Файл:** `js/tasks.js`

```javascript
// Аналогично clients.js, но для задач

async function loadTasks() {
    const status = document.getElementById('statusFilter').value;
    const priority = document.getElementById('priorityFilter').value;
    
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    
    const data = await api.get(`/api/tasks/?${params}`);
    renderTasks(data);
}

function renderTasks(tasks) {
    const container = document.getElementById('tasksList');
    
    container.innerHTML = tasks.map(task => `
        <div class="task-card" data-id="${task.id}">
            <div class="task-priority priority-${task.priority}"></div>
            <div class="task-content">
                <h3>${escapeHtml(task.title)}</h3>
                <p>${escapeHtml(task.description || '')}</p>
                <div class="task-meta">
                    <span class="task-status status-${task.status}">${getStatusLabel(task.status)}</span>
                    ${task.due_date ? `<span class="task-due">${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function getStatusLabel(status) {
    const labels = {
        'todo': 'К выполнению',
        'in_progress': 'В процессе',
        'done': 'Выполнено'
    };
    return labels[status] || status;
}
```

**Ожидаемый результат:** Страница задач работает

---

## Этап 4: Дашборд (Неделя 14)

### Задачи

#### 4.1 HTML страницы
**Файл:** `dashboard.html`

```html
<main class="main-content">
    <h1>Дашборд</h1>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="totalClients">—</div>
            <div class="stat-label">Всего клиентов</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" id="activeDeals">—</div>
            <div class="stat-label">Активных сделок</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" id="wonDeals">—</div>
            <div class="stat-label">Выиграно сделок</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" id="totalAmount">—</div>
            <div class="stat-label">Сумма выигранных</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" id="openTasks">—</div>
            <div class="stat-label">Открытых задач</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-value" id="overdueTasks">—</div>
            <div class="stat-label">Просроченных задач</div>
        </div>
    </div>
</main>
```

---

#### 4.2 JavaScript дашборда
**Файл:** `js/dashboard.js`

```javascript
async function loadDashboard() {
    try {
        const stats = await api.get('/api/dashboard/stats');
        renderStats(stats);
    } catch (error) {
        console.error('Ошибка загрузки дашборда:', error);
    }
}

function renderStats(stats) {
    document.getElementById('totalClients').textContent = stats.total_clients || 0;
    document.getElementById('activeDeals').textContent = stats.active_deals || 0;
    document.getElementById('wonDeals').textContent = stats.won_deals || 0;
    document.getElementById('totalAmount').textContent = formatMoney(stats.total_won_amount || 0);
    document.getElementById('openTasks').textContent = stats.open_tasks || 0;
    document.getElementById('overdueTasks').textContent = stats.overdue_tasks || 0;
}

loadDashboard();
```

---

#### 4.3 Стили дашборда
```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    text-align: center;
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary-color);
}

.stat-label {
    color: #666;
    margin-top: 0.5rem;
}
```

**Ожидаемый результат:** Дашборд работает

---

## Этап 5: Интеграция (Неделя 14-15)

### Задачи

#### 5.1 Тестирование
- Kanban доска работает
- Drag and Drop работает
- Задачи загружаются
- Дашборд показывает статистику

---

## Git Workflow

### Ветка
```
feature/frontend-deals-alexander
```

### Коммиты
```
feat: add deals page HTML
feat: add kanban styles
feat: add kanban drag and drop
feat: add tasks page
feat: add dashboard page
```

---

## Взаимодействие с командой

### С Дмитрием (Frontend Lead)
- Получение компонентов
- Помощь с API клиентом

### С Эвелиной (Backend - Deals)
- Получение документации по API сделок

### С Павлом (Backend - Tasks)
- Получение документации по API задач

---

## Критерии приёмки

- [ ] Kanban доска отображается
- [ ] Сделки по статусам в правильных колонках
- [ ] Drag and Drop работает
- [ ] При drop обновляется статус
- [ ] Страница задач работает
- [ ] Дашборд показывает статистику
- [ ] Фильтры работают

---

## Сроки

| Этап | Срок | Статус |
|------|------|--------|
| Подготовка | Неделя 1-2 | |
| Kanban доска | Неделя 13 | |
| Задачи | Неделя 13-14 | |
| Дашборд | Неделя 14 | |
| Интеграция | Неделя 14-15 | |

---

*При вопросах обращаться к Дмитрию (Frontend Lead)*
