import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "❌ Произошла ошибка при обработке вашего запроса.\n"
                "Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
        elif update.message:
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке вашего запроса.\n"
                "Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок: {str(e)}")
