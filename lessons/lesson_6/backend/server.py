"""Основной сервер с эндпоинтами"""
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils import user_manager

app = Flask('My server for study')
CORS(app)

# ==================== USERS ROUTES ====================

@app.route('/users', methods=['GET'])
def get_users():
    """Получить всех пользователей"""
    users = user_manager.get_all()
    return jsonify({
        'status': 'success',
        'count': user_manager.count(),
        'users': users
    }), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Получить пользователя по ID"""
    user = user_manager.get_by_id(user_id)

    if user:
        return jsonify({
            'status': 'success',
            'user': user
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': f'Пользователь с ID {user_id} не найден'
        }), 404


@app.route('/users', methods=['POST'])
def create_user():
    """Создать нового пользователя"""
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Content-Type должен быть application/json'
        }), 400

    data = request.get_json()

    # Валидация обязательных полей
    required_fields = ['name', 'email']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({
            'status': 'error',
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400

    # Проверка уникальности email
    if user_manager.email_exists(data['email']):
        return jsonify({
            'status': 'error',
            'message': 'Пользователь с таким email уже существует'
        }), 409

    # Создание пользователя
    new_user = user_manager.create(data)

    return jsonify({
        'status': 'success',
        'message': 'Пользователь успешно создан',
        'user': new_user
    }), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Обновить пользователя"""
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Content-Type должен быть application/json'
        }), 400

    data = request.get_json()

    # Проверка существования пользователя
    existing_user = user_manager.get_by_id(user_id)
    if not existing_user:
        return jsonify({
            'status': 'error',
            'message': f'Пользователь с ID {user_id} не найден'
        }), 404

    # Проверка уникальности email
    if 'email' in data and data['email'] != existing_user['email']:
        if user_manager.email_exists(data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Пользователь с таким email уже существует'
            }), 409

    # Обновление
    updated_user = user_manager.update(user_id, data)

    return jsonify({
        'status': 'success',
        'message': 'Пользователь успешно обновлен',
        'user': updated_user
    }), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Удалить пользователя"""
    deleted_user = user_manager.delete(user_id)

    if deleted_user:
        return jsonify({
            'status': 'success',
            'message': 'Пользователь успешно удален',
            'user': deleted_user
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': f'Пользователь с ID {user_id} не найден'
        }), 404


# ==================== FORM PROCESSING ====================

@app.route('/process-form', methods=['GET', 'POST'])
def process_form():
    """Обработка формы"""
    if request.method == 'POST':
        # Получаем данные из формы
        form_data = request.form.to_dict()

        # Или если данные в JSON формате
        if request.is_json:
            form_data = request.get_json()

        print("📝 Получены данные формы:", form_data)

        return jsonify({
            'status': 'success',
            'message': 'Данные формы успешно получены',
            'received_data': form_data
        }), 200

    return jsonify({
        'status': 'success',
        'message': 'GET запрос на /process-form',
        'method': 'GET'
    }), 200


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервера"""
    return jsonify({
        'status': 'healthy',
        'users_count': user_manager.count(),
        'timestamp': datetime.now().isoformat()
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Маршрут не найден'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Внутренняя ошибка сервера'
    }), 500


if __name__ == '__main__':
    from datetime import datetime

    print("🚀" * 30)
    print("🚀 Flask сервер запущен!")
    print("🚀" * 30)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📍 Доступные эндпоинты:")
    print("   " + "─" * 40)
    print("   📋 GET    /users           - все пользователи")
    print("   👤 GET    /users/<id>      - пользователь по ID")
    print("   ➕ POST   /users           - создать пользователя")
    print("   ✏️  PUT    /users/<id>      - обновить пользователя")
    print("   ❌ DELETE /users/<id>      - удалить пользователя")
    print("   📝 POST   /process-form    - обработать форму")
    print("   ❤️  GET    /health          - проверка сервера")
    print("   " + "─" * 40)
    print()
    print("💡 Данные хранятся в памяти (сбросятся при перезапуске)")
    print("💡 Формат даты: ISO 8601")
    print()
    print("🛑 Для остановки: Ctrl+C")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)