import logging
import time
import pandas as pd
import asyncio
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.excel_processor import ExcelProcessor
from services.zzap_api import ZzapAPI
from utils.formatters import format_progress_message
from handlers.auth import authorized_users

logger = logging.getLogger(__name__)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        if user_id not in authorized_users:
            await query.message.reply_text("❌ Необходима авторизация. Используйте /start")
            return

        if query.data == "upload_file":
            await query.message.reply_text(
                "📤 Пожалуйста, загрузите ваш Excel файл.\n"
                "Файл должен содержать колонки *catalog\\_article* и *brand*",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Ошибка в обработчике кнопки: {str(e)}")
        await query.message.reply_text(
            "❌ Произошла ошибка при обработке запроса.\n"
            "Пожалуйста, попробуйте еще раз или используйте /start"
        )

async def process_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загруженного файла"""
    user_id = update.effective_user.id

    if user_id not in authorized_users:
        await update.message.reply_text("❌ Необходима авторизация. Используйте /start")
        return

    try:
        if not update.message.document:
            await update.message.reply_text("❌ Пожалуйста, отправьте Excel файл.")
            return

        if not update.message.document.file_name.endswith(('.xlsx', '.xls')):
            await update.message.reply_text("❌ Поддерживаются только файлы Excel (.xlsx или .xls)")
            return

        file = await context.bot.get_file(update.message.document.file_id)
        input_bytes = io.BytesIO()
        await file.download_to_memory(input_bytes)
        input_bytes.seek(0)

        try:
            data = pd.read_excel(input_bytes)
        except Exception as e:
            logger.error(f"Ошибка чтения Excel файла: {str(e)}")
            await update.message.reply_text("❌ Ошибка чтения файла. Убедитесь, что файл в формате Excel и не поврежден.")
            return

        total_rows = len(data)
        if total_rows == 0:
            await update.message.reply_text("❌ Файл не содержит данных для обработки.")
            return

        processed_rows = 0
        last_update_time = time.time()
        update_interval = 0.5
        results = []

        progress_message = await update.message.reply_text(
            format_progress_message(processed_rows, total_rows, total_rows * 30)
        )

        for index, row in data.iterrows():
            partnumber = row.get("catalog_article")
            brand = row.get("brand")

            if pd.isna(partnumber) or pd.isna(brand):
                continue

            current_time = time.time()
            if current_time - last_update_time >= update_interval:
                remaining_time = (total_rows - processed_rows) * 30
                await progress_message.edit_text(
                    format_progress_message(processed_rows, total_rows, remaining_time)
                )
                last_update_time = current_time

            try:
                json_data = await ZzapAPI.get_part_info(partnumber, brand)
                results.append({
                    "Артикул": partnumber,
                    "Бренд": brand,
                    "Категория": json_data.get("class_cat", ""),
                    "Производитель": json_data.get("class_man", ""),
                    "Количество в наличии": json_data.get("price_count_instock", 0),
                    "Минимальная цена в наличии": json_data.get("price_min_instock", 0.0),
                    "Средняя цена в наличии": json_data.get("price_avg_instock", 0.0),
                    "Максимальная цена в наличии": json_data.get("price_max_instock", 0.0),
                    "Количество под заказ": json_data.get("price_count_order", 0),
                    "Минимальная цена под заказ": json_data.get("price_min_order", 0.0),
                    "Средняя цена под заказ": json_data.get("price_avg_order", 0.0),
                    "Максимальная цена под заказ": json_data.get("price_max_order", 0.0),
                })
                processed_rows += 1

            except Exception as e:
                logger.error(f"Ошибка обработки {partnumber} ({brand}): {str(e)}")
                await update.message.reply_text(f"⚠️ Ошибка обработки {partnumber} ({brand}): {str(e)}")

            await asyncio.sleep(30)

        await progress_message.edit_text(
            format_progress_message(processed_rows, total_rows, 0)
        )

        try:
            output_bytes = ExcelProcessor.create_result_excel(results)
        except Exception as e:
            logger.error(f"Ошибка создания Excel файла: {str(e)}")
            raise Exception("Ошибка при формировании итогового файла")

        keyboard = [[InlineKeyboardButton("📤 Загрузить новый файл", callback_data="upload_file")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        stats_message = (
            "📊 *Статистика обработки:*\n"
            f"• Всего строк: {total_rows}\n"
            f"• Обработано успешно: {len(results)}\n"
            f"• Пропущено: {total_rows - len(results)}\n\n"
            "✅ Обработка завершена!\n\n"
            "Нажмите кнопку ниже, чтобы загрузить новый файл."
        )

        try:
            await update.message.reply_document(
                document=output_bytes,
                filename="ZZAP_результат.xlsx",
                caption=stats_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка отправки файла: {str(e)}")
            raise Exception("Ошибка при отправке результата")

        await progress_message.delete()

    except Exception as e:
        error_message = f"❌ Произошла ошибка при обработке файла: {str(e)}"
        logger.error(error_message)

        keyboard = [[InlineKeyboardButton("🔄 Попробовать снова", callback_data="upload_file")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            error_message + "\n\nНажмите кнопку ниже, чтобы попробовать снова.",
            reply_markup=reply_markup
        )

        if 'progress_message' in locals():
            await progress_message.delete()
