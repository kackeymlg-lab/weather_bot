import telebot
import requests
import os
import logging
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

if not TOKEN or not OPENWEATHER_API_KEY:
    logger.error("❌ TELEGRAM_TOKEN или OPENWEATHER_API_KEY не установлены!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# ===== БД =====
DB_PATH = 'bot_stats.db'

def init_db():
    """Инициализация БД"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица запросов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT,
            temperature REAL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ БД инициализирована")

def save_user(user_id, username, first_name):
    """Сохранить пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения пользователя: {e}")

def save_request(user_id, city, temperature, description):
    """Сохранить запрос о погоде"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (user_id, city, temperature, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, city, temperature, description))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения запроса: {e}")

def get_stats():
    """Получить статистику"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Всего пользователей
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM requests')
        total_users = cursor.fetchone()[0]
        
        # Всего запросов
        cursor.execute('SELECT COUNT(*) FROM requests')
        total_requests = cursor.fetchone()[0]
        
        # Популярные города
        cursor.execute('''
            SELECT city, COUNT(*) as count 
            FROM requests 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        top_cities = cursor.fetchall()
        
        conn.close()
        
        return total_users, total_requests, top_cities
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        return 0, 0, []

# ===== КОМАНДЫ БОТА =====

@bot.message_handler(commands=['start'])
def start(message):
    """Команда /start"""
    user = message.from_user
    save_user(user.id, user.username, user.first_name)
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🌍 Москва', '🌤️ Санкт-Петербург')
    markup.add('☀️ Казань', '🌡️ Новосибирск')
    markup.add('📊 Статистика', '❓ Помощь')
    
    msg = f"👋 Привет, {user.first_name}!\n\nЯ помогу узнать прогноз погоды 🌤️"
    bot.send_message(message.chat.id, msg, reply_markup=markup)
    logger.info(f"✅ Пользователь {user.id} ({user.username}) начал чат")

@bot.message_handler(commands=['help'])
def help_command(message):
    """Команда /help"""
    msg = """
📚 **Доступные команды:**

🌍 **Выбери город** — нажми кнопку с городом
📊 **/stats** — вся статистика по боту
🔄 **/start** — начать заново
❓ **/help** — эта помощь

**Что я умею:**
✅ Показывать текущую погоду
✅ Сохранять историю запросов
✅ Показывать статистику
    """
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Команда /stats — показать статистику"""
    user = message.from_user
    save_user(user.id, user.username, user.first_name)
    
    total_users, total_requests, top_cities = get_stats()
    
    msg = f"""
📊 **СТАТИСТИКА БОТА:**

👥 Всего пользователей: **{total_users}**
🔄 Всего запросов: **{total_requests}**

🏆 **Топ городов:**
"""
    
    if top_cities:
        for i, (city, count) in enumerate(top_cities, 1):
            msg += f"\n{i}. {city} — {count} запросов"
    else:
        msg += "\n(Пока нет данных)"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    logger.info(f"✅ Статистика показана пользователю {user.id}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработка текстовых сообщений и кнопок"""
    user = message.from_user
    text = message.text
    save_user(user.id, user.username, user.first_name)
    
    # Предопределённые города
    cities = {
        '🌍 Москва': 'Moscow',
        '🌤️ Санкт-Петербург': 'Saint Petersburg',
        '☀️ Казань': 'Kazan',
        '🌡️ Новосибирск': 'Novosibirsk'
    }
    
    city_name = None
    city_key = None
    
    if text in cities:
        city_name = cities[text]
        city_key = text.split()[-1]  # Извлечь название города
    elif text == '📊 Статистика':
        stats_command(message)
        return
    elif text == '❓ Помощь':
        help_command(message)
        return
    else:
        city_name = text
        city_key = text
    
    try:
        # Запрос к OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            # Сохранить в БД
            save_request(user.id, city_key, temp, description)
            
            msg = f"""
🌍 **Погода в городе {city_key}**

🌡️ Температура: **{temp}°C**
📝 Описание: {description.capitalize()}
💧 Влажность: {humidity}%
💨 Ветер: {wind_speed} м/с
⏰ Время: {datetime.now().strftime('%H:%M:%S')}
            """
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
            logger.info(f"✅ Прогноз для {city_key} отправлен пользователю {user.id}")
        else:
            bot.send_message(message.chat.id, "❌ Город не найден. Попробуй ещё раз!")
            logger.warning(f"⚠️ Город '{city_name}' не найден")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        logger.error(f"❌ Ошибка при получении погоды: {e}")

# ===== ЗАПУСК БОТА =====

if __name__ == '__main__':
    logger.info("==================================================")
    logger.info("🤖 Бот запущен!")
    logger.info("==================================================")
    
    # Инициализация БД
    init_db()
    
    # Запуск бота
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
