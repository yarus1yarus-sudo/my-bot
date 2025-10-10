import requests
import json
import os
import time
import random

def load_config():
    """Загрузка конфигурации из config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        default_config = {
            'bot_enabled': True,
            'schedule': 'daily'
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config
    except:
        return {'bot_enabled': True, 'schedule': 'daily'}

def save_config(config):
    """Сохранение конфигурации в config.json"""
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения config.json: {e}")
        return False

# Получаем токены
ADMIN_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '').strip()
MAIN_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()

if not ADMIN_TOKEN:
    print("❌ ОШИБКА: ADMIN_BOT_TOKEN не найден!")
    exit(1)

ADMIN_CHAT_ID = "6396018806"

def send_message(text, reply_markup=None):
    """Отправка сообщения через админ-бота"""
    url = f"https://api.telegram.org/bot{ADMIN_TOKEN}/sendMessage"
    data = {
        'chat_id': ADMIN_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return False

def send_instant_joke():
    """Мгновенная отправка анекдота через основного бота"""
    if not MAIN_BOT_TOKEN:
        return False
        
    jokes = [
        "Почему программисты предпочитают тёмную тему? Потому что свет притягивает баги! 🐛",
        "— Доктор, у меня память как у рыбки! — А с каких пор? — Кто спрашивает? 🐠",
        "Жена программисту: — Дорогой, сходи в магазин за хлебом, и если будут яйца — купи дюжину. Программист приносит 12 батонов хлеба. 🥖",
        "Программист приходит домой в 3 утра. Жена: — Ты где был?! — На работе, отлаживал баги. — А я что, дура? — Нет, ты feature! ✨"
    ]
    
    joke = random.choice(jokes)
    
    url = f"https://api.telegram.org/bot{MAIN_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': ADMIN_CHAT_ID,
        'text': f"🎭 <b>Анекдот по запросу:</b>\n\n{joke}",
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_main_keyboard():
    """Основная клавиатура управления"""
    config = load_config()
    status = "🟢 Включен" if config.get('bot_enabled', True) else "🔴 Отключен"
    schedule = config.get('schedule', 'daily')
    
    schedule_text = {
        'daily': '📅 Ежедневно',
        '10m': '🕙 Каждые 10мин',
        '5m': '🕔 Каждые 5мин',
        '1m': '🕐 Каждую минуту'
    }.get(schedule, '📅 Ежедневно')
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': f'Статус: {status}', 'callback_data': 'status'}
            ],
            [
                {'text': '▶️ Включить', 'callback_data': 'start_bot'},
                {'text': '⏹️ Остановить', 'callback_data': 'stop_bot'}
            ],
            [
                {'text': '🎭 Анекдот сейчас!', 'callback_data': 'send_joke'}
            ],
            [
                {'text': f'⏰ {schedule_text}', 'callback_data': 'schedule_menu'}
            ]
        ]
    }
    return keyboard

def get_schedule_keyboard():
    """Клавиатура настройки расписания"""
    config = load_config()
    current = config.get('schedule', 'daily')
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '📅 Ежедневно' + (' ✅' if current == 'daily' else ''), 'callback_data': 'set_daily'}
            ],
            [
                {'text': '🕙 Каждые 10 минут' + (' ✅' if current == '10m' else ''), 'callback_data': 'set_10m'}
            ],
            [
                {'text': '🕔 Каждые 5 минут' + (' ✅' if current == '5m' else ''), 'callback_data': 'set_5m'}
            ],
            [
                {'text': '🕐 Каждую минуту' + (' ✅' if current == '1m' else ''), 'callback_data': 'set_1m'}
            ],
            [
                {'text': '🔙 Назад в меню', 'callback_data': 'back_to_menu'}
            ]
        ]
    }
    return keyboard

def handle_callback(callback_data):
    """Обработка нажатий кнопок"""
    config = load_config()
    
    if callback_data == 'start_bot':
        config['bot_enabled'] = True
        if save_config(config):
            print("✅ Бот включен через админ-панель")
            return "✅ Бот включен! Анекдоты будут отправляться по расписанию.", get_main_keyboard()
        else:
            return "❌ Ошибка включения бота", get_main_keyboard()
            
    elif callback_data == 'stop_bot':
        config['bot_enabled'] = False
        if save_config(config):
            print("🛑 Бот остановлен через админ-панель")
            return "🛑 Бот остановлен! Анекдоты отправляться не будут.", get_main_keyboard()
        else:
            return "❌ Ошибка остановки бота", get_main_keyboard()
    
    elif callback_data == 'send_joke':
        if send_instant_joke():
            return "🎭 Анекдот отправлен!", get_main_keyboard()
        else:
            return "❌ Ошибка отправки анекдота", get_main_keyboard()
            
    elif callback_data == 'schedule_menu':
        return "⏰ <b>Настройка расписания</b>\n\nВыберите частоту отправки анекдотов:", get_schedule_keyboard()
        
    elif callback_data.startswith('set_'):
        schedule_map = {
            'set_daily': 'daily',
            'set_10m': '10m', 
            'set_5m': '5m',
            'set_1m': '1m'
        }
        
        new_schedule = schedule_map.get(callback_data)
        if new_schedule:
            config['schedule'] = new_schedule
            if save_config(config):
                schedule_names = {
                    'daily': 'ежедневно',
                    '10m': 'каждые 10 минут',
                    '5m': 'каждые 5 минут', 
                    '1m': 'каждую минуту'
                }
                print(f"⏰ Расписание изменено на: {schedule_names[new_schedule]}")
                return f"⏰ Расписание изменено на: {schedule_names[new_schedule]}", get_schedule_keyboard()
        
        return "❌ Ошибка изменения расписания", get_schedule_keyboard()
        
    elif callback_data == 'back_to_menu':
        return "🎛️ <b>Панель управления ботом</b>\n\nВыберите действие:", get_main_keyboard()
            
    elif callback_data == 'status':
        status = "🟢 Включен" if config.get('bot_enabled', True) else "🔴 Отключен"
        schedule = config.get('schedule', 'daily')
        schedule_names = {
            'daily': 'ежедневно',
            '10m': 'каждые 10 минут',
            '5m': 'каждые 5 минут',
            '1m': 'каждую минуту'
        }
        return f"📊 <b>Статус системы:</b>\n• Бот: {status}\n• Расписание: {schedule_names.get(schedule, 'ежедневно')}", get_main_keyboard()
        
    return "❓ Неизвестная команда", get_main_keyboard()

def get_updates():
    """Получение обновлений от Telegram"""
    url = f"https://api.telegram.org/bot{ADMIN_TOKEN}/getUpdates"
    params = {'timeout': 30, 'offset': 0}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json().get('result', [])
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
    
    return []

def main():
    """Основная функция админ-бота"""
    print("🤖 Админ-бот запущен для управления...")
    
    # Отправляем панель управления
    welcome_text = "🎛️ <b>Панель управления ботом</b>\n\nВыберите действие:"
    keyboard = get_main_keyboard()
    
    if send_message(welcome_text, keyboard):
        print("✅ Панель управления отправлена")
    else:
        print("❌ Ошибка отправки панели")
    
    # Слушаем команды
    start_time = time.time()
    processed_updates = set()
    
    while time.time() - start_time < 3500:  # Почти час работы
        updates = get_updates()
        
        for update in updates:
            update_id = update.get('update_id')
            if update_id in processed_updates:
                continue
                
            processed_updates.add(update_id)
            
            # Обработка callback от кнопок
            if 'callback_query' in update:
                callback = update['callback_query']
                callback_data = callback.get('data', '')
                
                response_text, keyboard = handle_callback(callback_data)
                send_message(response_text, keyboard)
                print(f"📱 Обработан callback: {callback_data}")
            
            # Обработка команд /start
            elif 'message' in update:
                message = update['message']
                text = message.get('text', '').lower()
                
                if text in ['/start', '/menu']:
                    welcome_text = "🎛️ <b>Панель управления ботом</b>\n\nВыберите действие:"
                    keyboard = get_main_keyboard()
                    send_message(welcome_text, keyboard)
                    print("📝 Отправлено меню по команде")
        
        time.sleep(2)
    
    print("⏰ Время работы завершено")

if __name__ == "__main__":
    main()
