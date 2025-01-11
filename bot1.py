from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

CONTINENTS = [["Африка"], ["Азия"], ["Европа"], ["Северная Америка"], ["Южная Америка"], ["Австралия"]]

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

def main():
    import os
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
    application.run_polling()

if __name__ == "__main__":
    main()
