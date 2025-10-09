import requests
import json
import os
import random

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'bot_enabled': True, 'schedule': 'daily'}

# КЛЮЧЕВАЯ ПРОВЕРКА В САМОМ НАЧАЛЕ
config = load_config()
if not config.get('bot_enabled', False):
    print("🛑 Бот отключен через админ-панель. Выход.")
    exit()

print("✅ Бот включен, отправляем анекдот...")

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
USER_ID = "6396018806"

def get_joke():
    jokes = [
        "Почему программисты предпочитают тёмную тему? Потому что свет притягивает баги! 🐛",
        "— Доктор, у меня память как у рыбки! — А с каких пор? — Кто спрашивает? 🐠", 
        "Жена программисту: — Дорогой, сходи в магазин за хлебом, и если будут яйца — купи дюжину. Программист приносит 12 батонов хлеба. 🥖",
        "— Почему у программистов нет девушек? — Потому что они думают, что 1 + 1 = 10! 💻",
        "Программист приходит домой в 3 утра. Жена: — Ты где был?! — На работе, отлаживал баги. — А я что, дура? — Нет, ты feature! ✨"
    ]
    return random.choice(jokes)

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {'chat_id': USER_ID, 'text': text, 'parse_mode': 'HTML'}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    joke = get_joke()
    if send_message(f"😄 <b>Анекдот:</b>\n\n{joke}"):
        print("✅ Анекдот отправлен!")
    else:
        print("❌ Ошибка отправки!")
