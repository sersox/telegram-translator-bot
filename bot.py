from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Ваш существующий код бота...
# TOKEN = os.environ.get('BOT_TOKEN')  # Используйте переменные окружения
# ADMIN_ID = int(os.environ.get('ADMIN_ID'))import logging
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Загрузка конфигурации
load_dotenv("config.env")
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Настройка логирования
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

# Обработчик сообщений
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
        # Простая проверка на английский язык
        translated = translate_text(message.text)
        if translated and translated != message.text:
            reply = f"🔤 Перевод:\n{translated}"
            await message.reply_text(reply)
    except Exception as e:
        logger.error(f"Ошибка: {e}")

# Обработчик команды /setad
async def set_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_ID:
        global ADVERTISEMENT
        new_ad = " ".join(context.args)
        if new_ad:
            ADVERTISEMENT = new_ad
            await update.message.reply_text("✅ Рекламный текст обновлен!")
        else:
            await update.message.reply_text("❌ Укажите текст: /setad Ваш текст")
    else:
        await update.message.reply_text("🚫 Только администратор может менять рекламу")

# Рассылка рекламы
async def send_advertisement(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in active_chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=ADVERTISEMENT)
        except Exception as e:
            logger.error(f"Ошибка рассылки в чат {chat_id}: {e}")

# Обработчик для отслеживания чатов
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in active_chats:
        active_chats.add(chat_id)
        logger.info(f"Добавлен новый чат: {chat_id}")

# Главная функция
def main():
    # Создаем приложение с поддержкой JobQueue
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("setad", set_ad))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.ALL, track_chats))
    
    # Запускаем планировщик рекламы (каждые 2 часа)
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(send_advertisement, interval=7200, first=10)
    else:
        logger.warning("JobQueue не доступен. Рекламная рассылка отключена.")
    
    # Запускаем бота
    logger.info("Бот запускается...")
    application.run_polling()

if __name__ == '__main__':
    main()