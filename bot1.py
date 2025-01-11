import logging
import os
import json
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup

# Логирование
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Данные о континентах
CONTINENTS = [["Африка"], ["Азия"], ["Европа"], ["Северная Америка"], ["Южная Америка"], ["Австралия"]]

# Создаем бота
def create_application():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()
    return application

# Состояния и этапы разговора
async def start(update: Update, context):
    keyboard = [["Знаю точное место", "Не знаю точное место"]]
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

# Настройка FastAPI
app = FastAPI()

@app.post(f'/{os.getenv("TELEGRAM_BOT_TOKEN")}')
async def webhook(request: Request):
    json_str = await request.json()
    update = Update.de_json(json_str, bot)
    application.dispatcher.process_update(update)
    return {'status': 'ok'}

# Настройка бота
async def main():
    # Создаем бота
    application = create_application()

    # Добавляем обработчик команд
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

    # Устанавливаем вебхук
    bot = application.bot
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_URL')}/{os.getenv('TELEGRAM_BOT_TOKEN')}"
    await bot.set_webhook(url=webhook_url)  # Вызов с await, так как FastAPI поддерживает асинхронность

    # Запуск FastAPI
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
