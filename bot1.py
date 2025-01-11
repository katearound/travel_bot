import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from flask import Flask, request

# Логирование
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Континенты для выбора
CONTINENTS = [["Африка"], ["Азия"], ["Европа"], ["Северная Америка"], ["Южная Америка"], ["Австралия"]]
INTERESTS = [["Природа"], ["Активный отдых"], ["Архитектура"]]

# Состояния для ConversationHandler
(
    LOCATION,
    BUDGET,
    INTEREST,
    DURATION,
) = range(4)

async def start(update: Update, context):
    keyboard = [["Знаю точное место", "Не знаю точного места"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Привет! Куда вы хотите поехать?", reply_markup=reply_markup)
    return LOCATION

async def destination_choice(update: Update, context):
    choice = update.message.text
    if choice == "Знаю точное место":
        await update.message.reply_text("Введите название места:")
        return BUDGET
    else:
        reply_markup = ReplyKeyboardMarkup(CONTINENTS, one_time_keyboard=True)
        await update.message.reply_text("Выберите континент:", reply_markup=reply_markup)
        return LOCATION

async def exact_location(update: Update, context):
    place = update.message.text
    context.user_data["place"] = place  # Сохраняем место
    await update.message.reply_text(f"Вы выбрали {place}. Какой у вас бюджет на поездку?")
    return BUDGET

async def budget(update: Update, context):
    budget = update.message.text
    context.user_data["budget"] = budget  # Сохраняем бюджет
    await update.message.reply_text("Какие ваши интересы? Природа, активный отдых или архитектура?")
    reply_markup = ReplyKeyboardMarkup(INTERESTS, one_time_keyboard=True)
    return INTEREST

async def interest(update: Update, context):
    interest = update.message.text
    context.user_data["interest"] = interest  # Сохраняем интересы
    await update.message.reply_text("На сколько дней вы планируете поездку?")
    return DURATION

async def duration(update: Update, context):
    duration = update.message.text
    context.user_data["duration"] = duration  # Сохраняем сроки поездки
    # Отправляем итоговую информацию
    user_info = f"Место: {context.user_data['place']}\n" \
                f"Бюджет: {context.user_data['budget']}\n" \
                f"Интересы: {context.user_data['interest']}\n" \
                f"Сроки поездки: {context.user_data['duration']} дней"
    await update.message.reply_text(f"Спасибо за информацию!\n\nВот ваши данные:\n{user_info}")
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("Прощайте!")
    return ConversationHandler.END

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()

    # Настройка обработчика разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination_choice)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, exact_location)],
            INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, interest)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, duration)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Flask приложение для Render
    app = Flask(__name__)

    @app.route('/')
    def home():
        return 'Bot is running'

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        application.run_polling()

if __name__ == "__main__":
    main()
