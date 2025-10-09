import requests
import json
import os
import time

def load_config():
    """Загрузка конфигурации из config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Создаем файл с настройками по умолчанию
        default_config = {
            'bot_enabled': True,
            'schedule': 'daily'
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config
    except Exception as e:
        print(f"Ошибка загрузки config.json: {e}")
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

# Получаем токен с проверкой
ADMIN_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '').strip()
if not ADMIN_TOKEN:
    print("❌ ОШИБКА: ADMIN_BOT_TOKEN не найден!")
    exit(1)

ADMIN_CHAT_ID = "6396018806"

def send_message(text, reply_markup=None):
    """Отправка сообщения с кнопками"""
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

def get_keyboard():
    """Создание клавиатуры с кнопками управления"""
    config = load_config()
    status = "🟢 Включен" if config.get('bot_enabled', True) else "🔴 Отключен"
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': f'Статус бота: {status}', 'callback_data': 'status'}
            ],
            [
                {'text': '▶️ Включить бота', 'callback_data': 'start_bot'},
                {'text': '⏹️ Остановить бота', 'callback_data': 'stop_bot'}
            ],
            [
                {'text': '📊 Статистика', 'callback_data': 'stats'},
                {'text': '⚙️ Настройки', 'callback_data': 'settings'}
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
            return "✅ Бот включен! Анекдоты будут отправляться по расписанию."
        else:
            return "❌ Ошибка включения бота"
            
    elif callback_data == 'stop_bot':
        config['bot_enabled'] = False
        if save_config(config):
            return "🛑 Бот остановлен! Анекдоты отправляться не будут."
        else:
            return "❌ Ошибка остановки бота"
            
    elif callback_data == 'status':
        status = "🟢 Включен" if config.get('bot_enabled', True) else "🔴 Отключен"
        return f"📊 Текущий статус бота: {status}"
        
    elif callback_data == 'stats':
        return "📈 Статистика:\n• Сегодня отправлено: 1 анекдот\n• Статус: активен"
        
    elif callback_data == 'settings':
        return "⚙️ Настройки:\n• Расписание: ежедневно\n• Время: авто"
        
    return "❓ Неизвестная команда"

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
    print("🤖 Админ-бот запущен...")
    
    # Отправляем приветственное сообщение с кнопками
    welcome_text = "🎛️ <b>Панель управления ботом</b>\n\nВыберите действие:"
    keyboard = get_keyboard()
    
    if send_message(welcome_text, keyboard):
        print("✅ Панель управления отправлена")
    
    # Слушаем обновления
    start_time = time.time()
    processed_updates = set()
    
    while time.time() - start_time < 280:  # 4 мин 40 сек (до timeout 5 мин)
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
                
                response_text = handle_callback(callback_data)
                keyboard = get_keyboard()  # Обновляем клавиатуру
                
                send_message(response_text, keyboard)
                print(f"📱 Обработан callback: {callback_data}")
            
            # Обработка текстовых команд
            elif 'message' in update:
                message = update['message']
                text = message.get('text', '').lower()
                
                if text in ['/start', '/menu', 'меню']:
                    welcome_text = "🎛️ <b>Панель управления ботом</b>\n\nВыберите действие:"
                    keyboard = get_keyboard()
                    send_message(welcome_text, keyboard)
                    print("📝 Отправлено меню")
        
        time.sleep(2)  # Небольшая пауза между проверками
    
    print("⏰ Время работы истекло, завершаем...")

if __name__ == "__main__":
    main()
