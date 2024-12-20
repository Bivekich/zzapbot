from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import AUTH_TOKEN

authorized_users = set()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in authorized_users:
        await show_main_menu(update)
    else:
        await update.message.reply_text(
            "🔐 Добро пожаловать в ZZAP Parser Bot!\n\n"
            "Для начала работы, пожалуйста, введите токен авторизации в формате:\n"
            "/auth ваш_токен"
        )

async def auth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ Пожалуйста, укажите токен авторизации: /auth ваш_токен")
        return

    if context.args[0] == AUTH_TOKEN:
        authorized_users.add(user_id)
        await update.message.reply_text("✅ Авторизация успешна!")
        await show_main_menu(update)
    else:
        await update.message.reply_text("❌ Неверный токен авторизации. Попробуйте еще раз.")

async def show_main_menu(update: Update):
    keyboard = [[InlineKeyboardButton("📤 Загрузить Excel файл", callback_data="upload_file")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 *ZZAP Parser Bot*\n\n"
        "Этот бот поможет вам получить данные о запчастях из системы ZZAP.\n\n"
        "📋 *Инструкция:*\n"
        "1. Подготовьте Excel файл с колонками catalog\\_article и brand\n"
        "2. Нажмите кнопку ниже и загрузите файл\n"
        "3. Дождитесь обработки и получите результат\n\n"
        "🔍 Бот проанализирует каждую позицию и предоставит детальную информацию о ценах и наличии.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
