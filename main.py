import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config.settings import BOT_TOKEN
from handlers.auth import start_handler, auth_handler
from handlers.excel import button_callback, process_excel
from handlers.errors import error_handler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("auth", auth_handler))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.Document.ALL, process_excel))
        application.add_error_handler(error_handler)

        # Запуск бота
        print("🤖 Бот запущен и готов к работе!")
        application.run_polling()

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")

if __name__ == "__main__":
    main()
