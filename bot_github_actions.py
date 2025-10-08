import os
import json
import time
import requests
from bs4 import BeautifulSoup

# Загрузка конфигурации
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Если файла нет, создаём конфиг по умолчанию
        default_config = {
            "bot_enabled": True,
            "schedule_minutes": 15,
            "last_sent": 0,
            "admin_id": 6396018806,
            "version": "1.0"
        }
        save_config(default_config)
        return default_config

# Сохранение конфигурации
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Проверка нужно ли отправлять анекдот
def should_send_joke(config):
    if not config['bot_enabled']:
        print("⏸️ Бот остановлен по команде admin")
        return False
    
    current_time = int(time.time())
    last_sent = config['last_sent']
    interval_seconds = config['schedule_minutes'] * 60
    
    if current_time - last_sent >= interval_seconds:
        print(f"✅ Время отправки! Прошло {(current_time - last_sent) // 60} минут")
        return True
    else:
        remaining = ((last_sent + interval_seconds) - current_time) // 60
        print(f"⏰ Ещё не время. Осталось {remaining} минут")
        return False

def get_joke():
    # Резервные анекдоты на случай недоступности сайта
    backup_jokes = [
        "Программист — это человек, который решает проблемы, о существовании которых вы не подозревали, способами, которых вы не понимаете.",
        "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что 31 OCT = 25 DEC",
        "Жена программиста:\n— Дорогой, сходи в магазин за хлебом. И если будут яйца, купи десяток.\nПрограммист приходит домой с 10 буханками хлеба.\n— Зачем столько хлеба?!\n— Яйца были...",
        "Заходит программист в бар, заказывает пиво.\nБармен: — А пиво кончилось!\nПрограммист: — Тогда дайте что-нибудь еще.\nБармен: — А что еще?\nПрограммист: — Не знаю, у вас же меню должно быть!\nБармен: — Меню тоже кончилось.\nПрограммист: — Тогда зачем вы вообще здесь работаете?!\nБармен: — Я не работаю, я тоже программист, просто debugging делаю!",
        "— Сколько программистов нужно чтобы заменить лампочку?\n— Ноль. Это аппаратная проблема."
    ]
    
    try:
        # Добавляем заголовки чтобы сайт не блокировал запросы
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Получаем случайный анекдот
        response = requests.get('https://www.anekdot.ru/random/anekdot/', 
                              headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем div с классом text
            joke_div = soup.find('div', class_='text')
            if joke_div:
                joke_text = joke_div.get_text().strip()
                # Проверяем что анекдот не слишком короткий и не слишком длинный
                if len(joke_text) > 50 and len(joke_text) < 1000:
                    return joke_text
        
        # Если не получилось получить анекдот с сайта, берем из резерва
        import random
        return random.choice(backup_jokes)
        
    except Exception as e:
        print(f"Ошибка при получении анекдота: {e}")
        # В случае любой ошибки возвращаем случайный анекдот из резерва
        import random
        return random.choice(backup_jokes)

def send_to_telegram(message):
    bot_token = os.environ['BOT_TOKEN']
    channel_id = os.environ['CHANNEL_ID']
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    data = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data, timeout=30)
        if response.status_code == 200:
            print("✅ Анекдот успешно отправлен!")
            return True
        else:
            print(f"❌ Ошибка отправки: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False

def main():
    print("🤖 Проверка расписания...")
    config = load_config()
    
    if should_send_joke(config):
        joke = get_joke()
        message = f"😄 <b>Анекдот дня</b> 😄\n\n{joke}"
        
        if send_to_telegram(message):
            # Обновляем время последней отправки
            config['last_sent'] = int(time.time())
            save_config(config)
            print(f"📊 Обновлён config: последняя отправка {config['last_sent']}")
        else:
            print("❌ Не удалось отправить анекдот")
    else:
        print("⏭️ Пропускаем отправку")

if __name__ == "__main__":
    main()
