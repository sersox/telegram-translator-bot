import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

# Загрузка конфигурации
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Не установлен BOT_TOKEN")

# Создаем приложение бота
application = Application.builder().token(TOKEN).build()

# Простейший обработчик для Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Бот работает! Отправьте любой текст на английском для перевода.')

# Добавляем обработчик
application.add_handler(CommandHandler("start", start))

# Функция для запуска бота
def run_bot():
    print("Запуск бота...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling())

# Маршрут для проверки работы веб-сервера
@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Запуск бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    print("Бот запущен в фоновом режиме")
    
    # Запуск Flask сервера на правильном порту
    port = int(os.environ.get('PORT', 5000))
    print(f"Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)