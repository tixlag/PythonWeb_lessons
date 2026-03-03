const API_URL = '';

class ApiClient {
    constructor() {
        this.baseUrl = API_URL;
    }

    getToken() {
        /** это не безопасно. лучше хранить JWT токен в памяти приложения */
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