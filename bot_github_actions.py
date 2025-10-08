import os
import requests
from bs4 import BeautifulSoup

def get_joke():
    """Получить анекдот с сайта"""
    try:
        response = requests.get('https://anekdot.ru/random/anekdot/', timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        joke_element = soup.find('div', class_='text')
        if joke_element:
            return joke_element.get_text(strip=True)
    except:
        pass
    
    # Запасные анекдоты на случай проблем с сайтом
    backup_jokes = [
        "Программист пришёл домой. Жена говорит:\n- Сходи в магазин, купи хлеб, а если будут яйца - возьми десяток.\nПрограммист пришёл и принёс 10 батонов хлеба.\n- Зачем столько хлеба?\n- Ну так яйца же были...",
        "- Доктор, я забываю всё через 5 секунд!\n- Это серьёзно. Давно это у вас?\n- Что давно?",
        "Учитель спрашивает:\n- Петя, если у твоего папы есть 10 яблок и он даст половину маме, сколько останется у папы?\n- 10, Марья Ивановна!\n- Петя, ты не умеешь делить!\n- Нет, это вы не знаете моего папу!"
    ]
    import random
    return random.choice(backup_jokes)

def send_to_telegram(message):
    """Отправить сообщение в Telegram канал"""
    bot_token = os.environ['BOT_TOKEN']
    channel_id = os.environ['CHANNEL_ID']
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ Анекдот успешно отправлен!")
    else:
        print(f"❌ Ошибка отправки: {response.status_code}")
        print(response.text)

def main():
    joke = get_joke()
    message = f"😄 <b>Анекдот дня</b> 😄\n\n{joke}"
    send_to_telegram(message)

if __name__ == "__main__":
    main()
