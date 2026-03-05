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