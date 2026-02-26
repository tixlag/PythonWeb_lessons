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

column.addEventListener('drop', async (e) => {
    e.preventDefault();
    const dealId = e.dataTransfer.getData('text/plain');
    if (!dealId) return; // нет данных – ничего не делаем

    const newStatus = column.dataset.status;
    const currentCard = document.querySelector(`.deal-card[data-id="${dealId}"]`);
    const currentStatus = currentCard?.dataset.status;

    // Если статус не изменился, не отправляем запрос
    if (currentStatus === newStatus) return;

    await updateDealStatus(dealId, newStatus);
});