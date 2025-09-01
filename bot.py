import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Хранилище состояния пользователей
user_data = {}

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Твой chat_id:", update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("Fortnite", callback_data="game_Fortnite")],
        [InlineKeyboardButton("GTA 5", callback_data="game_GTA 5")],
        [InlineKeyboardButton("EA SPORTS FC™ Mobile Soccer", callback_data="game_EA SPORTS FC™ Mobile Soccer")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите игру из списка по кнопке, затем опишите задачу, и подтвердите отправку заявки.",
        reply_markup=reply_markup
    )
    user_data[update.effective_user.id] = {"stage": "choose_game"}


# --- Обработка кнопок выбора игры ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data.startswith("game_"):
        game = query.data.split("_", 1)[1]
        user_data[user_id] = {"stage": "describe_task", "game": game}

        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"Ваша игра: {game}. Опишите задачу подробно.",
            reply_markup=reply_markup
        )

    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("Fortnite", callback_data="game_Fortnite")],
            [InlineKeyboardButton("GTA 5", callback_data="game_GTA 5")],
            [InlineKeyboardButton("EA SPORTS FC™ Mobile Soccer", callback_data="game_EA SPORTS FC™ Mobile Soccer")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        user_data[user_id] = {"stage": "choose_game"}

        await query.edit_message_text(
            text="Выберите игру из списка по кнопке, затем опишите задачу, и подтвердите отправку заявки.",
            reply_markup=reply_markup
        )

    elif query.data == "confirm":
        game = user_data[user_id].get("game")
        task = user_data[user_id].get("task")

        await query.edit_message_text(text="✅ Заявка отправлена! Ожидайте сообщение от исполнителя!")

        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Новая заявка!\nИгра: {game}\nЗадача: {task}\nОт: @{query.from_user.username or query.from_user.id}"
            )


        user_data[user_id] = {"stage": "choose_game"}  # сброс

    elif query.data == "edit":
        keyboard = [
            [InlineKeyboardButton("Fortnite", callback_data="game_Fortnite")],
            [InlineKeyboardButton("GTA 5", callback_data="game_GTA 5")],
            [InlineKeyboardButton("EA SPORTS FC™ Mobile Soccer", callback_data="game_EA SPORTS FC™ Mobile Soccer")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        user_data[user_id] = {"stage": "choose_game"}

        await query.edit_message_text(
            text="Выберите игру из списка по кнопке, затем опишите задачу, и подтвердите отправку заявки.",
            reply_markup=reply_markup
        )


# --- Обработка текстовых сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data or user_data[user_id].get("stage") != "describe_task":
        return

    user_data[user_id]["task"] = text

    game = user_data[user_id].get("game")

    keyboard = [
        [InlineKeyboardButton("Да, отправить", callback_data="confirm")],
        [InlineKeyboardButton("Нет, изменить", callback_data="edit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Заявка по игре {game}: {text}\nВсё верно?",
        reply_markup=reply_markup
    )
    user_data[user_id]["stage"] = "confirming"


# --- Запуск бота ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
