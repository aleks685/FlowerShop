from telegram import Update
from telegram.ext import ContextTypes

from keyboards import (
    get_occasion_keyboard,
    get_color_keyboard,
    get_price_keyboard,
)


async def start_picker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text="Для какого повода нужен букет? 🌸",
        reply_markup=get_occasion_keyboard()
    )


async def handle_occasion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    occasion = query.data.replace("occasion_", "")
    context.user_data["occasion"] = occasion

    await query.edit_message_text(
        text="Выберите цветовую гамму 🌸",
        reply_markup=get_color_keyboard()
    )


async def handle_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    color = query.data.replace("color_", "")
    context.user_data["color"] = color

    await query.edit_message_text(
        text="Выберите бюджет 🌸",
        reply_markup=get_price_keyboard()
    )
    