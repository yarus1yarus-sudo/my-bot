import os
import json
import time
import requests
from urllib.parse import quote

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "bot_enabled": True,
            "schedule_minutes": 15,
            "last_sent": 0,
            "admin_id": 6396018806,
            "version": "1.0"
        }

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def send_telegram_message(message, chat_id, reply_markup=None):
    token = os.getenv('ADMIN_BOT_TOKEN')
    if not token:
        print("❌ ADMIN_BOT_TOKEN не найден!")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

def create_main_menu():
    """Создает главное меню с кнопками"""
    return {
        "inline_keyboard": [
            [
                {"text": "🟢 Запустить бот", "callback_data": "start_bot"},
                {"text": "🔴 Остановить бот", "callback_data": "stop_bot"}
            ],
            [
                {"text": "⏰ Изменить время", "callback_data": "schedule_menu"},
                {"text": "📊 Статус бота", "callback_data": "status"}
            ],
            [
                {"text": "😄 Отправить анекдот", "callback_data": "send_joke"},
                {"text": "🔄 Обновить меню", "callback_data": "refresh"}
            ]
        ]
    }

def create_schedule_menu():
    """Создает меню выбора времени"""
    return {
        "inline_keyboard": [
            [
                {"text": "5 мин", "callback_data": "schedule_5"},
                {"text": "10 мин", "callback_data": "schedule_10"},
                {"text": "15 мин", "callback_data": "schedule_15"}
            ],
            [
                {"text": "30 мин", "callback_data": "schedule_30"},
                {"text": "1 час", "callback_data": "schedule_60"},
                {"text": "2 часа", "callback_data": "schedule_120"}
            ],
            [
                {"text": "🔙 Назад", "callback_data": "main_menu"}
            ]
        ]
    }

def process_callback(callback_data, chat_id, config):
    """Обрабатывает нажатия кнопок"""
    
    if chat_id != config['admin_id']:
        send_telegram_message("❌ У вас нет прав для управления ботом!", chat_id)
        return config
    
    if callback_data == "start_bot":
        config['bot_enabled'] = True
        save_config(config)
        send_telegram_message("🟢 <b>Бот ЗАПУЩЕН!</b>\n\n✅ Анекдоты будут отправляться по расписанию", chat_id, create_main_menu())
        
    elif callback_data == "stop_bot":
        config['bot_enabled'] = False
        save_config(config)
        send_telegram_message("🔴 <b>Бот ОСТАНОВЛЕН!</b>\n\n❌ Анекдоты НЕ будут отправляться", chat_id, create_main_menu())
        
    elif callback_data == "status":
        status = "🟢 РАБОТАЕТ" if config['bot_enabled'] else "🔴 ОСТАНОВЛЕН"
        last_sent = "Никогда" if config['last_sent'] == 0 else time.strftime("%d.%m.%Y %H:%M", time.localtime(config['last_sent']))
        
        message = f"""📊 <b>СТАТУС БОТА</b>
        
🤖 Состояние: {status}
⏰ Интервал: {config['schedule_minutes']} минут
📅 Последний анекдот: {last_sent}
👤 Админ ID: {config['admin_id']}
📦 Версия: {config['version']}"""
        
        send_telegram_message(message, chat_id, create_main_menu())
        
    elif callback_data == "schedule_menu":
        send_telegram_message("⏰ <b>Выберите интервал отправки:</b>", chat_id, create_schedule_menu())
        
    elif callback_data.startswith("schedule_"):
        minutes = int(callback_data.split("_")[1])
        config['schedule_minutes'] = minutes
        save_config(config)
        
        hours_text = ""
        if minutes >= 60:
            hours = minutes // 60
            hours_text = f" ({hours} ч.)" if hours == 1 else f" ({hours} ч.)"
            
        send_telegram_message(f"⏰ <b>Расписание изменено!</b>\n\n✅ Новый интервал: {minutes} минут{hours_text}", chat_id, create_main_menu())
        
    elif callback_data == "send_joke":
        send_telegram_message("😄 <b>Команда отправлена!</b>\n\n🚀 Анекдот будет отправлен при следующем запуске бота", chat_id, create_main_menu())
        config['last_sent'] = 0  # Сбрасываем время для принудительной отправки
        save_config(config)
        
    elif callback_data == "main_menu" or callback_data == "refresh":
        send_telegram_message("🎛️ <b>ПАНЕЛЬ УПРАВЛЕНИЯ БОТОМ</b>\n\nВыберите действие:", chat_id, create_main_menu())
    
    return config

def process_command(command, chat_id, config):
    """Обрабатывает текстовые команды"""
    
    if chat_id != config['admin_id']:
        send_telegram_message("❌ У вас нет прав для управления ботом!", chat_id)
        return config
    
    if command in ['/start', '/help', '/menu']:
        welcome_message = f"""🎛️ <b>ПАНЕЛЬ УПРАВЛЕНИЯ БОТОМ</b>

👋 Добро пожаловать, Админ!

🤖 Бот для отправки анекдотов
🎯 Управление через кнопки ниже

Выберите действие:"""
        
        send_telegram_message(welcome_message, chat_id, create_main_menu())
    
    return config

def main():
    print("🚀 Админ-бот запущен...")
    
    token = os.getenv('ADMIN_BOT_TOKEN')
    if not token:
        print("❌ ADMIN_BOT_TOKEN не найден!")
        return
    
    offset = 0
    start_time = time.time()
    timeout_duration = 300  # 5 минут
    
    config = load_config()
    
    while time.time() - start_time < timeout_duration:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {'offset': offset, 'timeout': 10}
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['ok'] and data['result']:
                    for update in data['result']:
                        offset = update['update_id'] + 1
                        
                        # Обработка текстовых сообщений
                        if 'message' in update:
                            message = update['message']
                            chat_id = message['chat']['id']
                            text = message.get('text', '')
                            
                            print(f"📨 Получено сообщение: {text} от {chat_id}")
                            config = process_command(text, chat_id, config)
                        
                        # Обработка нажатий кнопок
                        elif 'callback_query' in update:
                            callback = update['callback_query']
                            chat_id = callback['from']['id']
                            callback_data = callback['data']
                            
                            print(f"🔘 Нажата кнопка: {callback_data} от {chat_id}")
                            
                            # Отвечаем на callback_query
                            callback_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                            requests.post(callback_url, data={'callback_query_id': callback['id']})
                            
                            config = process_callback(callback_data, chat_id, config)
            
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
    
    print("⏰ Время работы админ-бота истекло")

if __name__ == "__main__":
    main()
