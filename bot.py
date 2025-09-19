import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler

app = Flask(__name__)

# Загрузка конфигурации
TOKEN = os.environ.get('BOT_TOKEN')

# Простейший обработчик для Telegram
async def start(update, context):
    await update.message.reply_text('Бот работает!')

# Маршрут для проверки работы веб-сервера
@app.route('/')
def home():
    return "Telegram Bot is running!"

# Функция для запуска бота в отдельном потоке
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    # Запуск бота в фоновом режиме
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запуск Flask сервера
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)