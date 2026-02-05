"""Вспомогательные функции для работы с пользователями"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class UserManager:
    """Менеджер пользователей (хранение в памяти)"""

    def __init__(self):
        self.users: List[Dict[str, Any]] = []
        self.next_id: int = 1

        # Инициализация тестовых пользователей при запуске
        self._initialize_default_users()

    def _initialize_default_users(self):
        """Инициализация 3 тестовых пользователей"""
        now = datetime.now().isoformat()

        default_users = [
            {
                'id': 1,
                'name': 'Иван Петров',
                'email': 'ivan@example.com',
                'age': 30,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': 2,
                'name': 'Мария Сидорова',
                'email': 'maria@example.com',
                'age': 25,
                'created_at': now,
                'updated_at': now
            },
            {
                'id': 3,
                'name': 'Алексей Козлов',
                'email': 'alex@example.com',
                'age': 35,
                'created_at': now,
                'updated_at': now
            }
        ]

        self.users = default_users
        self.next_id = 4  # Следующий ID будет 4

    def get_all(self) -> List[Dict[str, Any]]:
        """Получить всех пользователей"""
        return self.users

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        return next((u for u in self.users if u['id'] == user_id), None)

    def create(self,  data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать нового пользователя"""
        now = datetime.now().isoformat()

        user = {
            'id': self.next_id,
            'name': data['name'],
            'email': data['email'],
            'age': data.get('age'),
            'created_at': now,
            'updated_at': now
        }

        self.users.append(user)
        self.next_id += 1
        return user

    def update(self, user_id: int,  data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить пользователя"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            user['email'] = data['email']
        if 'age' in data:
            user['age'] = data['age']

        user['updated_at'] = datetime.now().isoformat()
        return user

    def delete(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Удалить пользователя"""
        user = self.get_by_id(user_id)
        if user:
            self.users.remove(user)
            return user
        return None

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Проверить, существует ли email"""
        for user in self.users:
            if user['email'] == email:
                if exclude_id is None or user['id'] != exclude_id:
                    return True
        return False

    def count(self) -> int:
        """Получить количество пользователей"""
        return len(self.users)


# Глобальный экземпляр (синглтон для всего приложения)
user_manager = UserManager()