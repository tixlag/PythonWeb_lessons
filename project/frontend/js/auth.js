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

        const cred = `username=${username}&password=${password}`

        const response = await fetch(`${api.baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: cred
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