from flask import Flask, request, jsonify
import os
import json
import random
import string
import telebot

app = Flask(__name__)
USERS_DIR = "users"

# Если директории для пользователей не существует, создаём её
if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# Словарь для хранения проверочных кодов (в тестовом режиме, в памяти)
verification_codes = {}

# Настройте вашего Telegram-бота (замените YOUR_TELEGRAM_BOT_TOKEN на настоящий токен)
bot_token = "7106954059:AAGexddglYQLRoXAF1RUcW9SCyKeaX7LAA0"
bot = telebot.TeleBot(token=bot_token)

def get_user_file(nickname):
    return os.path.join(USERS_DIR, f"{nickname}.json")

@app.route('/register', methods=['POST'])
def register():
    """
   регистрация
    жду JSON с полями: nickname, password, name, avatar (в base64).
    создаю файл nickname.json с начальными статистиками (wins=0, losses=0, win_rate=0.0).
    """
    data = request.json
    nickname = data.get('nickname')
    password = data.get('password')
    name = data.get('name')
    avatar = data.get('avatar')
    
    if not all([nickname, password, name, avatar]):
        return jsonify({'error': 'Ошибка! Недостаточно информации, проверьте важные поля'}), 400

    user_file = get_user_file(nickname)
    if os.path.exists(user_file):
        return jsonify({'error': 'Ошибка! Такой UserName уже существует'}), 400

    user_data = {
        "nickname": nickname,
        "name": name,
        "password": password,
        "avatar": avatar,
        "wins": 0,
        "losses": 0,
        "win_rate": 0.0
    }
    
    with open(user_file, "w") as f:
        json.dump(user_data, f)

    return jsonify({'message': 'Регистрация прошла успешно!'}), 200

@app.route('/login', methods=['POST'])
def login():
    """
   авторизация
    жду JSON с полями: nickname и password.
    в случае если файл пользователя существует и пароль совпадает – возвращается HTTP 200.
    """
    data = request.json
    nickname = data.get('nickname')
    password = data.get('password')
    
    if not nickname or not password:
        return jsonify({'error': 'Ошибка! Недостаточно информации для входа'}), 400

    user_file = get_user_file(nickname)
    if not os.path.exists(user_file):
        return jsonify({'error': 'Ошибка! Пользователь не найден'}), 404

    with open(user_file, "r") as f:
        user_data = json.load(f)

    if user_data.get("password") != password:
        return jsonify({'error': 'Ошибка! Неверные учетные данные'}), 401

    return jsonify({'message': 'Вход выполнен успешно!'}), 200

@app.route('/update_stats', methods=['POST'])
def update_stats():
    """
   обновление статистики
    жду JSON с полями: nickname, wins, losses.
    пересчитываю процент побед (win_rate).
    """
    data = request.json
    nickname = data.get('nickname')
    wins = data.get('wins')
    losses = data.get('losses')

    if not nickname or wins is None or losses is None:
        return jsonify({'error': 'Ошибка! Недостаточно данных для обновления статистики'}), 400

    user_file = get_user_file(nickname)
    if not os.path.exists(user_file):
        return jsonify({'error': 'Ошибка! Пользователь не найден'}), 404

    with open(user_file, "r") as f:
        user_data = json.load(f)

    user_data['wins'] = wins
    user_data['losses'] = losses
    total = wins + losses
    user_data['win_rate'] = (wins / total * 100) if total > 0 else 0.0

    with open(user_file, "w") as f:
        json.dump(user_data, f)

    return jsonify({'message': 'Статистика пользователя успешно обновлена'}), 200

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    """
   Лидерборд
    поля: nickname, name, avatar, wins, losses, win_rate.
    Выводит данные в формате:
      {
          "results": [ { ... }, { ... }, ... ]
      }
    Список сортируется по проценту побед (win_rate) в порядке убывания.
    """
    results = []
    for filename in os.listdir(USERS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(USERS_DIR, filename), "r") as f:
                user_data = json.load(f)
                results.append({
                    "nickname": user_data.get("nickname"),
                    "name": user_data.get("name"),
                    "avatar": user_data.get("avatar"),
                    "wins": user_data.get("wins"),
                    "losses": user_data.get("losses"),
                    "win_rate": user_data.get("win_rate")
                })
    results.sort(key=lambda x: x['win_rate'], reverse=True)
    return jsonify({"results": results}), 200

@app.route('/search', methods=['GET'])
def search_users():
    """
   поиск пользователей
    жду GET-параметр 'nickname'.
    Ищу пользователей, чье поле nickname содержит переданную подстроку (без учета регистра).
    Возвращаю данные в формате:
      {
          "results": [ { ... }, { ... }, ... ]
      }
    """
    query = request.args.get('nickname')
    if not query:
        return jsonify({'error': 'Ошибка! Не указан параметр поиска'}), 400

    results = []
    for filename in os.listdir(USERS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(USERS_DIR, filename), "r") as f:
                user_data = json.load(f)
                if query.lower() in user_data.get("nickname", "").lower():
                    results.append({
                        "nickname": user_data.get("nickname"),
                        "name": user_data.get("name"),
                        "avatar": user_data.get("avatar"),
                        "wins": user_data.get("wins"),
                        "losses": user_data.get("losses"),
                        "win_rate": user_data.get("win_rate")
                    })
    return jsonify({"results": results}), 200

# --- Эндпоинты для бота по telegram_id ---

@app.route('/send_code_bot', methods=['POST'])
def send_code_bot():
    """
   отправка проверочного кода через бота
    жду параметры через form: telegram_id.
    Генерирую случайный 6-значный код и отправляю сообщение через Telegram-бота по переданному chat_id.
    """
    telegram_id = request.form.get('telegram_id')
    if not telegram_id:
        return jsonify({'error': 'Ошибка! Не указан telegram_id'}), 400
    
    # Убеждаемся, что telegram_id можно привести к целому числу
    try:
        chat_id = int(telegram_id)
    except ValueError:
        return jsonify({'error': 'Ошибка! telegram_id должен быть числом'}), 400

    # Генерируем 6-значный код
    code = ''.join(random.choices(string.digits, k=6))
    try:
        bot.send_message(chat_id=chat_id, text=f"Ваш проверочный код: {code}")
    except Exception as e:
        return jsonify({'error': f'Ошибка отправки сообщения через бота: {e}'}), 500
    
    # Сохраняем код в памяти для telegram_id (ключ – строковое представление id)
    verification_codes[str(chat_id)] = code
    return jsonify({'message': 'Проверочный код отправлен через бота'}), 200

@app.route('/verify_code_bot', methods=['POST'])
def verify_code_bot():
    """
   проверка проверочного кода, отправленного через бота
    жду параметры через form: telegram_id, code.
    Сравниваю присланный код с сохранённым для данного telegram_id.
    """
    telegram_id = request.form.get('telegram_id')
    code = request.form.get('code')
    if not telegram_id or not code:
        return jsonify({'error': 'Ошибка! Не указан telegram_id или код'}), 400

    try:
        chat_id = int(telegram_id)
    except ValueError:
        return jsonify({'error': 'Ошибка! telegram_id должен быть числом'}), 400

    stored_code = verification_codes.get(str(chat_id))
    if stored_code is None:
        return jsonify({'error': 'Ошибка! Код для этого telegram_id не найден'}), 404

    if code == stored_code:
        return jsonify({'message': 'Код подтвержден'}), 200
    else:
        return jsonify({'error': 'Ошибка! Неверный код'}), 401

if __name__ == '__main__':
    app.run(debug=True)
