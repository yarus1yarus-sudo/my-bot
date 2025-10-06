import requests
import os
from bs4 import BeautifulSoup
import random
from datetime import datetime

def get_joke():
    """Получает случайный анекдот с проверенного источника"""
    try:
        url = "https://anekdot.ru/random/anekdot/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        jokes = soup.find_all('div', class_='text')
        
        if jokes:
            joke = random.choice(jokes)
            joke_text = joke.get_text(strip=True)
            # Ограничиваем длину
            if len(joke_text) > 500:
                joke_text = joke_text[:500] + "..."
            return joke_text
        else:
            return get_backup_joke()
            
    except Exception as e:
        print(f"Ошибка при получении анекдота: {e}")
        return get_backup_joke()

def get_backup_joke():
    """Резервные анекдоты"""
    backup_jokes = [
        "— Доктор, у меня проблемы с памятью.\n— Когда это началось?\n— Что началось?",
        "Программист приходит домой.\nЖена:\n— Сходи в магазин, купи хлеб. Если будут яйца — купи десяток.\nПрограммист приносит 10 буханок хлеба.\n— Зачем столько хлеба?!\n— Яйца были...",
        "— Алло, это зоопарк?\n— Да.\n— Сбежал слон?\n— Нет.\n— А жаль, а то у меня в огороде кто-то картошку копает...",
        "Встречаются два друга:\n— Как дела?\n— Отлично! Вчера выиграл в лотерею миллион!\n— Поздравляю! И что будешь делать?\n— Буду покупать билеты, пока не проиграю...",
        "— Доктор, что со мной?\n— Вам нужен полный покой.\n— А что это значит?\n— Ну... жена должна уехать к маме на месяц."
    ]
    return random.choice(backup_jokes)

def send_to_telegram(message):
    """Отправляет сообщение в Telegram канал"""
    bot_token = os.environ['BOT_TOKEN']
    channel_id = os.environ['CHANNEL_ID']
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": channel_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print("✅ Сообщение успешно отправлено!")
            return True
        else:
            print(f"❌ Ошибка API Telegram: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False

def main():
    """Основная функция - отправляет один анекдот"""
    print(f"🤖 Запуск бота анекдотов - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Получаем анекдот
    joke = get_joke()
    print(f"📖 Получен анекдот: {joke[:50]}...")
    
    # Форматируем сообщение
    current_time = datetime.now().strftime('%H:%M')
    message = f"🎭 <b>Анекдот дня</b> ({current_time})\n\n{joke}\n\n#анекдот #юмор"
    
    # Отправляем
    if send_to_telegram(message):
        print("🎉 Задача выполнена успешно!")
    else:
        print("❌ Не удалось отправить анекдот")

if __name__ == "__main__":
    main()
