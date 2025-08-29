from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import re
import logging
import os
import pymysql
import json
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv("all.env")
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  
    "database": "chatMJFWbot",
    "charset": "utf8mb4",
    "cursorclass": DictCursor
}

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

with open("banned_words.json", "r", encoding="utf-8") as file:
    BANNED_WORDS = json.load(file)

def initialize_database():
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id BIGINT PRIMARY KEY,
                language VARCHAR(10) DEFAULT 'en'
            )
            """
        )
        connection.commit()
    connection.close()

def get_chat_settings(chat_id):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM chat_settings WHERE chat_id = %s", (chat_id,))
        settings = cursor.fetchone()
    connection.close()
    return settings

def update_chat_settings(chat_id, language):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO chat_settings (chat_id, language)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            language = VALUES(language)
            """,
            (chat_id, language)
        )
        connection.commit()
    connection.close()

MESSAGES = {
    "start": {
        "en": "Hello! I am a moderation bot. I am here to keep this chat clean.",
        "ru": "Привет! Я бот-модератор. Я здесь, чтобы поддерживать порядок в этом чате."
    },
    "message_deleted": {
        "en": "Message from {user} was deleted due to prohibited content.",
        "ru": "Сообщение пользователя {user} было удалено из-за содержания запрещённых слов."
    },
    "temp_ban": {
        "en": "User {user} has been temporarily banned for 1 hour.",
        "ru": "Пользователь {user} получил временный бан на 1 час."
    },
    "temp_ban_error": {
        "en": "Failed to temporarily ban user: {error}",
        "ru": "Не удалось временно забанить пользователя: {error}."
    }
}

def get_user_language(update: Update):
    return update.effective_user.language_code[:2] if update.effective_user.language_code else "en"

async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    settings = get_chat_settings(chat_id)
    lang = settings["language"] if settings else "en"
    message = MESSAGES["start"].get(lang, MESSAGES["start"]["en"])
    await update.message.reply_text(message)

async def filter_messages(update: Update, context: CallbackContext):
    if update.message.from_user.is_bot:
        logger.info("Message ignored: sent by another bot.")
        return

    chat_id = update.message.chat_id
    settings = get_chat_settings(chat_id)
    lang = settings["language"] if settings else "en"
    banned_words = BANNED_WORDS.get(lang, [])

    message = update.message.text.lower()

    logger.info(f"Checking message: {message} for banned words: {banned_words}")

    for word in banned_words:
        if word in message:
            try:
                await update.message.delete()
                warning = MESSAGES["message_deleted"].get(lang, MESSAGES["message_deleted"]["en"])
                await update.message.reply_text(warning.format(user=update.message.from_user.first_name))
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")

async def temp_ban(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    settings = get_chat_settings(chat_id)
    lang = settings["language"] if settings else "en"

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=60 * 60
            )
            ban_message = MESSAGES["temp_ban"].get(lang, MESSAGES["temp_ban"]["en"])
            await update.message.reply_text(ban_message.format(user=update.message.reply_to_message.from_user.first_name))
        except Exception as e:
            error_message = MESSAGES["temp_ban_error"].get(lang, MESSAGES["temp_ban_error"]["en"])
            await update.message.reply_text(error_message.format(error=e))

if __name__ == "__main__":
    import asyncio
    initialize_database()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("temp_ban", temp_ban))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.run_polling())
