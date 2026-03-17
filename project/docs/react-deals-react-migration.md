# React и модуль сделок: почему это меняет фронтенд

Ниже — учебный разбор в роли преподавателя. Мы сравним текущий модуль сделок на Vanilla JS и покажем, как React решает его слабые места. В конце — пошаговая инструкция подключения React (Vite + React, без TypeScript) и примеры кода.

---

## 1. Что именно изменил React во фронтенде

React изменил подход от «ручного обновления DOM» к «декларативному UI». Мы больше не говорим браузеру *как* менять HTML, мы описываем *каким должен быть интерфейс*, а React сам приводит DOM к нужному состоянию.

Ключевые идеи:
- **Состояние как источник истины**: UI = f(state)
- **Компонентная архитектура**: интерфейс как набор повторно используемых блоков
- **Однонаправленный поток данных**: родитель → дети через `props`
- **Минимальные изменения DOM**: React сам высчитывает «дельту»

На практике это значит: меньше кода, меньше ошибок синхронизации, проще масштабировать интерфейс.

---

## 2. Слабые места Vanilla JS в модуле сделок

Смотрим на реальные файлы:
- `frontend/js/deals.js`
- `frontend/deals.html`

### 2.1 Ручной рендеринг и «полная перерисовка»
В `renderDeals()` сначала очищаются все колонки, затем всё рендерится заново:
- `document.querySelectorAll('.column-content').forEach(... col.innerHTML = '')`
- снова создаются карточки и вставляются в DOM

Проблемы:
- интерфейс «моргает»
- много лишней работы браузера
- сложнее сделать частичное обновление

### 2.2 Разрыв между данными и UI
Состояние сделок живет «в DOM». Нет единого массива `deals` как источника истины:
- UI отражает данные, но сами данные не хранятся централизованно
- любое изменение в UI требует ручного поиска DOM-элементов

### 2.3 Сложная синхронизация после действий
При перетаскивании сделки:
- `updateDealStatus()` вызывает `loadDeals()`
- весь список перезагружается

Это простой, но не масштабируемый подход:
- лишние запросы
- сложно внедрить оптимистичные обновления

### 2.4 Глобальные зависимости и порядок скриптов
`deals.js` опирается на `clients` из `clients.js`:
- `clients` — глобальная переменная
- важно, чтобы `clients.js` загрузился раньше
- открыть модалку до загрузки клиентов → баги

### 2.5 Ручные обработчики и трудность повторного использования
В Vanilla JS каждое событие вешается вручную:
- `addEventListener('dragstart', ...)`
- `addEventListener('drop', ...)`

В итоге:
- логика размазана по коду
- сложно переиспользовать карточку в другом месте

---

## 3. Как React решает эти проблемы

### Проблема 1: Полная перерисовка
**React-решение:** рендер по состоянию. Меняется только то, что реально изменилось.

### Проблема 2: Разрыв между UI и данными
**React-решение:** единый `state` — источник истины.

### Проблема 3: Синхронизация после действий
**React-решение:** оптимистичное обновление + выборочный рефетч.

### Проблема 4: Глобальные переменные
**React-решение:** данные передаются как `props` или живут в `state`.

### Проблема 5: Размазанная логика
**React-решение:** компонентная архитектура, логика локализована.

---

## 4. Инструкция по подключению React (Vite + React JS)

### Шаг 1. Создать отдельный фронтенд-пакет
```bash
npm create vite@latest frontend-react -- --template react
cd frontend-react
npm install
```

### Шаг 2. Структура проекта
```text
frontend-react/
├── src/
│   ├── api/
│   │   └── apiClient.js
│   ├── components/
│   │   ├── DealCard.jsx
│   │   ├── DealModal.jsx
│   │   └── KanbanColumn.jsx
│   ├── pages/
│   │   └── DealsPage.jsx
│   ├── hooks/
│   │   └── useDeals.js
│   └── main.jsx
```

### Шаг 3. Подключить API-клиент
Смысл тот же, что и в `frontend/js/api.js`, но в формате модуля:

```js
// src/api/apiClient.js
export async function apiGet(url) {
  const res = await fetch(url, { credentials: 'include' });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiPost(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    credentials: 'include'
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiPut(url, data) {
  const res = await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
    credentials: 'include'
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

### Шаг 4. Перенести страницу сделок
Создаем страницу `DealsPage.jsx`.

---

## 5. Пример решения на React (модуль сделок)

### 5.1 Хук для сделок
```jsx
// src/hooks/useDeals.js
import { useEffect, useState } from 'react';
import { apiGet, apiPut, apiPost } from '../api/apiClient';

export function useDeals() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadDeals() {
    setLoading(true);
    try {
      const data = await apiGet('/api/deals/');
      setDeals(data);
    } finally {
      setLoading(false);
    }
  }

  async function updateStatus(id, status) {
    // оптимистично обновляем UI
    setDeals(prev => prev.map(d => d.id === id ? { ...d, status } : d));
    await apiPut(`/api/deals/${id}`, { status });
  }

  async function createDeal(payload) {
    await apiPost('/api/deals/', payload);
    await loadDeals();
  }

  useEffect(() => {
    loadDeals();
  }, []);

  return { deals, loading, updateStatus, createDeal, reload: loadDeals };
}
```

### 5.2 Канбан-страница
```jsx
// src/pages/DealsPage.jsx
import { useMemo } from 'react';
import { useDeals } from '../hooks/useDeals';
import KanbanColumn from '../components/KanbanColumn';

const STATUSES = ['new', 'negotiation', 'won', 'lost'];

export default function DealsPage() {
  const { deals, loading, updateStatus } = useDeals();

  const grouped = useMemo(() => {
    const map = { new: [], negotiation: [], won: [], lost: [] };
    deals.forEach(d => map[d.status].push(d));
    return map;
  }, [deals]);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="kanban-board">
      {STATUSES.map(status => (
        <KanbanColumn
          key={status}
          status={status}
          deals={grouped[status]}
          onDropDeal={updateStatus}
        />
      ))}
    </div>
  );
}
```

### 5.3 Колонка
```jsx
// src/components/KanbanColumn.jsx
import DealCard from './DealCard';

export default function KanbanColumn({ status, deals, onDropDeal }) {
  function handleDrop(e) {
    e.preventDefault();
    const dealId = Number(e.dataTransfer.getData('text/plain'));
    if (!dealId) return;
    onDropDeal(dealId, status);
  }

  return (
    <div className="kanban-column" data-status={status}>
      <div className="column-header">
        <h3>{status}</h3>
        <span className="deal-count">{deals.length}</span>
      </div>
      <div
        className="column-content"
        onDragOver={e => e.preventDefault()}
        onDrop={handleDrop}
      >
        {deals.map(deal => (
          <DealCard key={deal.id} deal={deal} />
        ))}
      </div>
    </div>
  );
}
```

### 5.4 Карточка сделки
```jsx
// src/components/DealCard.jsx
export default function DealCard({ deal }) {
  function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', String(deal.id));
  }

  return (
    <div className="deal-card" draggable onDragStart={handleDragStart}>
      <div className="deal-title">{deal.title}</div>
      <div className="deal-amount">{deal.amount}</div>
      <div className="deal-client">{deal.client?.name || '—'}</div>
    </div>
  );
}
```

---

## 6. Итог: что реально упростилось

Сравним задачи:
- **Vanilla JS:** ручное обновление DOM, сложное управление событиями, глобальные зависимости.
- **React:** стейт → UI, компонентная структура, простое масштабирование.

Итог как преподаватель: React не делает «магии», он убирает ручной труд. Это освобождает разработчика для логики продукта, а не борьбы с DOM.

---

## 7. Рекомендации студентам

1. Пройдитесь по `frontend/js/deals.js` и отметьте места, где вы «вручную управляете DOM».
2. Сравните это с React-компонентами: где стало меньше кода и почему.
3. Сделайте упражнение: добавить новый статус (например `pending`) в обеих версиях и сравнить сложность.

---

Если нужно — могу дополнить материал архитектурной схемой React-слоя или предложить следующий шаг: перенос модуля клиентов.
