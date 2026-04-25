from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from keyboards import get_consent_keyboard, get_main_menu_keyboard
from picker_flow import (
    start_picker,
    handle_occasion,
    handle_color,
    handle_price
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with open("FlowerShop privacy policy.pdf", "rb") as file:
        await update.message.reply_document(
            document=file,
            caption="Политика конфиденциальности FlowerShop 🌸"
        )

    await update.message.reply_text(
        "Пожалуйста, подтвердите согласие на обработку персональных данных.",
        reply_markup=get_consent_keyboard()
    )


async def handle_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    if query.data == "agree":
        await query.edit_message_text(
            text="Спасибо 🌸\n\nВыберите действие:",
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "disagree":
        await query.edit_message_text(
            text="Без согласия мы не можем продолжить работу."
        )


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        await query.edit_message_text("Каталог скоро будет") # каталог листинг файлов 

    elif query.data == "choose_bouquet":
        await start_picker(update, context) # подбор букета дальше picker_flow.py

    elif query.data == "consultation":
        await query.edit_message_text("Флорист скоро свяжется") # звнок флориста 


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(handle_consent, pattern="^(agree|disagree)$")
    )

    app.add_handler(
        CallbackQueryHandler(
            handle_main_menu,
            pattern="^(catalog|choose_bouquet|consultation)$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(handle_occasion, pattern="^occasion_")
    )

    app.add_handler(
        CallbackQueryHandler(handle_color, pattern="^color_")
    )

    app.add_handler(
        CallbackQueryHandler(handle_price, pattern="^price_")
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()