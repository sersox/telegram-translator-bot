import os
import asyncio
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
from deep_translator import GoogleTranslator

# Инициализация Flask приложения
app = Flask(__name__)

# Загрузка конфигурации
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

# Настройка логирования
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные
ADVERTISEMENT = "🌟 Пользуйтесь нашим ботом! Отличный переводчик! 🌟"
active_chats = set()

# Функция перевода
def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='ru').translate(text)
    except Exception as e:
        logger.error(f"Ошибка перевода: {e}")
        return None

# Обработчики команд и сообщений
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Бот работает! Отправьте текст на английском для перевода.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    message = update.message
    user = message.from_user
    
    # Игнорируем сообщения от ботов и команды
    if user.is_bot or message.text.startswith('/'):
        return
    
    # Пытаемся перевести текст
    try:
        translated = translate_text(message.text)
        if translated and translated != message.text:
            reply = f"🔤 Перевод:\n{translated}"
            await message.reply_text(reply)
    except Exception as e:
        logger.error(f"Ошибка: {e}")

# Создаем и настраиваем приложение бота
def setup_bot():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

# Маршрут для проверки работоспособности
@app.route('/')
def home():
    return "Telegram Bot is running!"

# Запуск бота
async def main():
    application = setup_bot()
    await application.run_polling()

# Запуск Flask приложения
if __name__ == '__main__':
    # Запускаем бота в фоновом режиме
    import threading
    thread = threading.Thread(target=lambda: asyncio.run(main()))
    thread.daemon = True
    thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)