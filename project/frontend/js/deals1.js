const STATUSES = ['new', 'negotiation', 'won', 'lost'];

if (!auth.isAuthenticated()) {
    window.location.href = '/login.html';
}

let currentDeals = [];

// Загрузка сделок
async function loadDeals() {
    try {
        const data = await api.get('/api/deals/');
        currentDeals = data;
        renderDeals(data);
    } catch (error) {
        console.error('Ошибка загрузки сделок:', error);
        alert('Ошибка загрузки сделок: ' + error.message);
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
        <div class="deal-actions">
            <button class="btn-edit" data-id="${deal.id}">Редактировать</button>
            <button class="btn-delete" data-id="${deal.id}">Удалить</button>
        </div>
    `;

    // Drag events
    card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', e.target.dataset.id);
        e.target.classList.add('dragging');
    });

    card.addEventListener('dragend', (e) => {
        e.target.classList.remove('dragging');
    });

    card.querySelector('.btn-edit').addEventListener('click', (e) => {
        e.stopPropagation();
        openEditModal(deal);
    });

    card.querySelector('.btn-delete').addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm(`Удалить сделку "${deal.title}"?`)) {
            deleteDeal(deal.id);
        }
    });

    return card;
}

async function deleteDeal(dealId) {
    try {
        await api.delete(`/deals/${dealId}`);
        await loadDeals();
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
}

function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.id);
    e.target.classList.add('dragging');
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

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

(async function () {
    await loadDeals();
})();


// Настройка drop зон
document.querySelectorAll('.column-content').forEach(column => {
    column.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    column.addEventListener('drop', async (e) => {
        e.preventDefault();
        const dealId = e.dataTransfer.getData('text/plain');
        const newStatus = column.dataset.status;
        const deal = currentDeals.find(d => d.id == dealId);
        if (!deal || deal.status === newStatus) return; // нет данных – ничего не делаем

        try {
            await api.put(`/deals/${dealId}`, { status: newStatus });
            await loadDeals();
        } catch (error) {
            alert('Ошибка обновления статуса: ' + error.message);
        }
    });
});


function openEditModal(deal) {
    document.getElementById('editTitle').value = deal.title;
    document.getElementById('editClientId').value = deal.client_id;
    document.getElementById('editAmount').value = deal.amount;
    document.getElementById('editStatus').value = deal.status;
    document.getElementById('editAssignedTo').value = deal.assigned_to || '';
    
    document.getElementById('saveEditBtn').dataset.dealId = deal.id;
    
    document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

async function saveEdit() {
    const dealId = document.getElementById('saveEditBtn').dataset.dealId;
    const formData = {
        title: document.getElementById('editTitle').value,
        client_id: parseInt(document.getElementById('editClientId').value),
        amount: parseFloat(document.getElementById('editAmount').value),
        status: document.getElementById('editStatus').value,
        assigned_to: document.getElementById('editAssignedTo').value ? 
            parseInt(document.getElementById('editAssignedTo').value) : null
    };
    
    try {
        await api.put(`/deals/${dealId}`, formData);
        closeEditModal();
        await loadDeals();
        alert('Сделка успешно обновлена');
    } catch (error) {
        alert('Ошибка обновления: ' + error.message);
    }
}


