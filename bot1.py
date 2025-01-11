import logging
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from flask import Flask, request

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Континенты для выбора
CONTINENTS = [["Африка"], ["Азия"], ["Европа"], ["Северная Америка"], ["Южная Америка"], ["Австралия"]]

# Создание экземпляра Flask
app = Flask(__name__)

# Инициализация бота
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

# Асинхронная функция для установки webhook
async def set_webhook():
    webhook_url = f"https://travel-bot-22jb.onrender.com/{os.getenv('TELEGRAM_BOT_TOKEN')}"
    await bot.set_webhook(url=webhook_url)

# Обработчик команд
async def start(update: Update, context):
    keyboard = [["Знаю точное место", "Не знаю точного места"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Привет! Куда вы хотите поехать?", reply_markup=reply_markup)
    return 1

async def destination_choice(update: Update, context):
    choice = update.message.text
    if choice == "Знаю точное место":
        await update.message.reply_text("Введите название места:")
        return 2
    else:
        reply_markup = ReplyKeyboardMarkup(CONTINENTS, one_time_keyboard=True)
        await update.message.reply_text("Выберите континент:", reply_markup=reply_markup)
        return 3

async def exact_location(update: Update, context):
    place = update.message.text
    await update.message.reply_text(f"Отлично, вы выбрали {place}!")
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("Прощайте!")
    return ConversationHandler.END

# Обработчик webhook
@app.route(f'/{os.getenv("TELEGRAM_BOT_TOKEN")}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)  # Используем глобальный объект bot
    application.update_queue.put(update)
    return 'ok', 200

# Настройка бота и webhook
async def main():
    # Токен бота
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination_choice)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, exact_location)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, exact_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Настроить webhook
    await set_webhook()

    # Запуск Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
