import os
import json
import requests
import time
from datetime import datetime

# Загрузка конфигурации
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Создаём конфиг по умолчанию
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

# Отправка сообщения в Telegram
def send_telegram_message(message, chat_id):
    bot_token = os.environ.get('ADMIN_BOT_TOKEN')
    if not bot_token:
        print("❌ ADMIN_BOT_TOKEN не найден!")
        return False
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

# Получение анекдота (копия из основного бота)
def get_joke():
    backup_jokes = [
        "Программист — это человек, который решает проблемы, о существовании которых вы не подозревали, способами, которых вы не понимаете.",
        "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что 31 OCT = 25 DEC",
        "Жена программиста:\n— Дорогой, сходи в магазин за хлебом. И если будут яйца, купи десяток.\nПрограммист приходит домой с 10 буханками хлеба.\n— Зачем столько хлеба?!\n— Яйца были...",
        "Заходит программист в бар, заказывает пиво.\nБармен: — А пиво кончилось!\nПрограммист: — Тогда дайте что-нибудь еще.\nБармен: — А что еще?\nПрограммист: — Не знаю, у вас же меню должно быть!\nБармен: — Меню тоже кончилось.\nПрограммист: — Тогда зачем вы вообще здесь работаете?!\nБармен: — Я не работаю, я тоже программист, просто debugging делаю!",
        "— Сколько программистов нужно чтобы заменить лампочку?\n— Ноль. Это аппаратная проблема."
    ]
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get('https://www.anekdot.ru/random/anekdot/', 
                              headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем div с классом text
            joke_div = soup.find('div', class_='text')
            if joke_div:
                joke_text = joke_div.get_text().strip()
                if len(joke_text) > 50 and len(joke_text) < 1000:
                    return joke_text
        
        # Если не получилось, возвращаем случайный из резерва
        import random
        return random.choice(backup_jokes)
        
    except Exception as e:
        print(f"❌ Ошибка получения анекдота: {e}")
        import random
        return random.choice(backup_jokes)

# Отправка анекдота в канал
def send_joke_to_channel():
    joke = get_joke()
    message = f"😄 <b>Анекдот дня</b> 😄\n\n{joke}"
    
    channel_id = os.environ.get('CHANNEL_ID')
    bot_token = os.environ.get('BOT_TOKEN')
    
    if not bot_token or not channel_id:
        return False, "❌ Токены не найдены"
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data, timeout=30)
        return response.status_code == 200, joke
    except Exception as e:
        return False, str(e)

# Обработка команд
def process_command(command, chat_id, config):
    if chat_id != config['admin_id']:
        send_telegram_message("❌ У вас нет прав для управления ботом!", chat_id)
        return config
    
    if command == '/start':
        config['bot_enabled'] = True
        save_config(config)
        send_telegram_message("✅ <b>Бот включён!</b>\n\n🤖 Анекдоты будут отправляться автоматически", chat_id)
    
    elif command == '/stop':
        config['bot_enabled'] = False
        save_config(config)
        send_telegram_message("⏸️ <b>Бот остановлен!</b>\n\n🛑 Автоотправка анекдотов отключена", chat_id)
    
    elif command == '/status':
        status = "✅ Включён" if config['bot_enabled'] else "⏸️ Остановлен"
        last_sent = datetime.fromtimestamp(config['last_sent']).strftime('%d.%m.%Y %H:%M') if config['last_sent'] > 0 else "Никогда"
        
        message = f"""📊 <b>Статус бота:</b>
        
🤖 <b>Состояние:</b> {status}
⏰ <b>Интервал:</b> {config['schedule_minutes']} минут
📤 <b>Последняя отправка:</b> {last_sent}
🔢 <b>Версия:</b> {config['version']}"""
        
        send_telegram_message(message, chat_id)
    
    elif command.startswith('/schedule '):
        try:
            minutes = int(command.split()[1])
            if 1 <= minutes <= 10080:  # от 1 минуты до недели
                config['schedule_minutes'] = minutes
                save_config(config)
                
                if minutes < 60:
                    time_str = f"{minutes} минут"
                elif minutes < 1440:
                    time_str = f"{minutes // 60} часов"
                else:
                    time_str = f"{minutes // 1440} дней"
                
                send_telegram_message(f"⏰ <b>Расписание изменено!</b>\n\n📅 Новый интервал: {time_str}", chat_id)
            else:
                send_telegram_message("❌ Интервал должен быть от 1 минуты до 7 дней (10080 минут)", chat_id)
        except (ValueError, IndexError):
            send_telegram_message("❌ Неверный формат! Используйте: /schedule 30", chat_id)
    
    elif command == '/joke':
        success, result = send_joke_to_channel()
        if success:
            config['last_sent'] = int(time.time())
            save_config(config)
            send_telegram_message(f"✅ <b>Анекдот отправлен в канал!</b>\n\n📝 <i>{result[:100]}...</i>", chat_id)
        else:
            send_telegram_message(f"❌ <b>Ошибка отправки:</b>\n\n{result}", chat_id)
    
    elif command == '/help':
        help_text = """🎛️ <b>Команды управления ботом:</b>

🚀 <b>/start</b> — включить автоотправку
⏸️ <b>/stop</b> — остановить автоотправку  
📊 <b>/status</b> — текущее состояние
⏰ <b>/schedule [минуты]</b> — изменить интервал
😄 <b>/joke</b> — отправить анекдот сейчас
❓ <b>/help</b> — эта справка

<b>Примеры расписания:</b>
• <code>/schedule 15</code> — каждые 15 минут
• <code>/schedule 60</code> — каждый час
• <code>/schedule 1440</code> — каждый день"""
        
        send_telegram_message(help_text, chat_id)
    
    else:
        send_telegram_message("❌ Неизвестная команда! Используйте /help", chat_id)
    
    return config

# Получение обновлений от Telegram
def get_updates(offset=0):
    bot_token = os.environ.get('ADMIN_BOT_TOKEN')
    if not bot_token:
        print("❌ ADMIN_BOT_TOKEN не найден!")
        return []
    
    url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
    params = {'offset': offset, 'timeout': 30}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json().get('result', [])
    except Exception as e:
        print(f"❌ Ошибка получения обновлений: {e}")
    
    return []

def main():
    print("🎛️ Admin Bot запущен!")
    config = load_config()
    last_update_id = 0
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            
            for update in updates:
                last_update_id = update['update_id']
                
                if 'message' in update:
                    message = update['message']
                    chat_id = message['chat']['id']
                    text = message.get('text', '')
                    
                    if text.startswith('/'):
                        print(f"📥 Команда: {text} от {chat_id}")
                        config = process_command(text, chat_id, config)
        
        except KeyboardInterrupt:
            print("\n⏹️ Admin Bot остановлен")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
