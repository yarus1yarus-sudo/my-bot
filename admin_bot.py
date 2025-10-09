import requests
import json
import os
import random

# Функция для загрузки конфигурации
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Если файл не существует, создаем его с настройками по умолчанию
        default_config = {
            'bot_enabled': True,
            'schedule': 'daily'
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config
    except json.JSONDecodeError:
        print("Ошибка чтения config.json. Используем настройки по умолчанию.")
        return {'bot_enabled': True, 'schedule': 'daily'}

# КЛЮЧЕВАЯ ПРОВЕРКА: Читаем конфигурацию в самом начале
config = load_config()
if not config.get('bot_enabled', False):
    print("🛑 Бот отключен в config.json. Выход из программы.")
    exit()

print("✅ Бот включен. Начинаем работу...")

# Получаем токен из переменных окружения
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден в переменных окружения")
    exit()

# ID пользователя для отправки анекдотов
USER_ID = "6396018806"

# Функция для получения анекдота
def get_joke():
    jokes = [
        "Почему программисты предпочитают тёмную тему? Потому что свет притягивает баги! 🐛",
        "— Доктор, у меня память как у рыбки! — А с каких пор? — Кто спрашивает? 🐠",
        "Жена программисту: — Дорогой, сходи в магазин за хлебом, и если будут яйца — купи дюжину. Программист приносит 12 батонов хлеба. 🥖",
        "— Почему у программистов нет девушек? — Потому что они думают, что 1 + 1 = 10! 💻",
        "Идёт программист по улице и видит лягушку. Лягушка говорит: — Поцелуй меня, и я стану прекрасной принцессой! Программист берёт лягушку и кладёт в карман. — Почему ты меня не поцеловал? — А зачем мне принцесса? Говорящая лягушка круче! 🐸",
        "— Мам, а что такое рекурсия? — Иди спроси у папы. — Пап, а что такое рекурсия? — Иди спроси у мамы. 🔄",
        "Программист приходит домой в 3 утра. Жена: — Ты где был?! — На работе, отлаживал баги. — А я что, дура? — Нет, ты feature! ✨",
        "Встречаются два программиста: — Как дела? — Как в аду! — То есть как? — 0 и 1! 😈",
        "— Доктор, помогите! Я думаю, что я компьютер! — Хм, интересно. А как давно это началось? — С момента загрузки... то есть рождения! 💾",
        "Программист ложится спать. Мозг: — А ты точно закрыл все скобки? Программист встаёт проверять код... 🧠"
    ]
    return random.choice(jokes)

# Функция для отправки сообщения
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': USER_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        print(f"✅ Анекдот отправлен успешно!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке анекдота: {e}")
        return False

# Основная логика
if __name__ == "__main__":
    print("🤖 Запуск бота для отправки анекдота...")
    
    # Получаем анекдот
    joke = get_joke()
    print(f"📝 Выбран анекдот: {joke[:50]}...")
    
    # Отправляем анекдот
    if send_message(f"😄 <b>Анекдот дня:</b>\n\n{joke}"):
        print("🎉 Задача выполнена!")
    else:
        print("💥 Задача провалена!")
