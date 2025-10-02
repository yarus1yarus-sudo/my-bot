import requests
import random
import logging
import os
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Резервные анекдоты на случай проблем с парсингом
FALLBACK_JOKES = [
    "Программист приходит домой, а жена говорит:\n— Иди в магазин, купи хлеб, а если будут яйца — возьми десяток.\nПрограммист приходит с десятью буханками хлеба:\n— Дорогая, яйца были!",
    
    "— Доктор, я забываю всё сразу после того, как выхожу от вас!\n— И давно у вас это?\n— Что у меня?",
    
    "Муж жене:\n— Дорогая, я ухожу в магазин.\n— Хорошо, купи молока.\n— А если не будет молока?\n— Тогда не уходи в магазин.",
    
    "Встречаются два программиста:\n— Как дела?\n— Да вот, баги фиксю...\n— А что за баги?\n— Да фичи такие...",
    
    "— Алло, это служба экстренного вызова слесаря?\n— Да.\n— У меня кран не закрывается!\n— А вы пробовали крутить его по часовой стрелке?\n— Пробовал...\n— А против часовой?\n— Тоже пробовал...\n— А вы пробовали выключить его и включить заново?"
]

def get_joke_from_anekdot_ru():
    """Получить анекдот с сайта anekdot.ru"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get('https://www.anekdot.ru/random/anekdot/', headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем анекдот по CSS селектору
        joke_element = soup.select_one('.text')
        
        if joke_element:
            joke_text = joke_element.get_text(strip=True)
            # Очищаем текст от лишних символов
            joke_text = joke_text.replace('\n\n', '\n').strip()
            
            if len(joke_text) > 50:  # Проверяем, что это не пустой текст
                logger.info(f"Получен анекдот с anekdot.ru: {joke_text[:50]}...")
                return joke_text
        
        logger.warning("Не удалось извлечь анекдот с anekdot.ru")
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при получении анекдота с anekdot.ru: {e}")
        return None

def get_random_fallback_joke():
    """Получить случайный анекдот из резервного списка"""
    joke = random.choice(FALLBACK_JOKES)
    logger.info("Используется резервный анекдот")
    return joke

def get_joke():
    """Получить анекдот (сначала попробовать с сайта, потом резервный)"""
    # Пробуем получить с anekdot.ru
    joke = get_joke_from_anekdot_ru()
    
    if joke:
        return joke
    
    # Если не получилось, используем резервный
    return get_random_fallback_joke()

def send_to_telegram(text, bot_token, channel_id):
    """Отправить сообщение в Telegram канал"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': channel_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        logger.info("Анекдот успешно отправлен в Telegram")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}")
        return False

def main():
    """Основная функция - отправить один анекдот"""
    # Получаем конфигурацию из переменных окружения
    bot_token = os.environ.get('BOT_TOKEN')
    channel_id = os.environ.get('CHANNEL_ID')
    
    if not bot_token:
        logger.error("BOT_TOKEN не найден в переменных окружения")
        return False
        
    if not channel_id:
        logger.error("CHANNEL_ID не найден в переменных окружения")
        return False
    
    logger.info("Запуск отправки анекдота")
    
    # Получаем анекдот
    joke = get_joke()
    
    if not joke:
        logger.error("Не удалось получить анекдот")
        return False
    
    # Отправляем в Telegram
    success = send_to_telegram(joke, bot_token, channel_id)
    
    if success:
        logger.info(f"Анекдот отправлен: {joke[:100]}...")
        return True
    else:
        logger.error("Не удалось отправить анекдот")
        return False

if __name__ == "__main__":
    main()
