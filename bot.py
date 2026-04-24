import datetime

from dotenv import load_dotenv
from environs import Env
from telegram import ReplyKeyboardMarkup, update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

from keyboards import get_consent_keyboard, get_main_menu_keyboard

env = Env()
load_dotenv()

BOT_TOKEN = env.str('TG_BOT_TOKEN')

# состояния диалога
START, MAIN_MENU, CATALOG, EVENT_CHOICE, BOUQUET_MENU, COLOR_CHOICE, PRICE_CHOICE, \
    CONSULTATION, SAVE_NAME, SAVE_PHONE, SAVE_ADDRESS, DELIVERY, SAVE_DATE, \
    ORDER_CONFIRM, PAYMENT_CHOICE = range(15)

client_contacts = []


def start(update, context):
    update.message.reply_text("Подтвердите согласие на обработку персональных данных "
                              "в соответствии с политикой конфиденциальности.",
                              reply_markup=get_consent_keyboard())
    return START


def main_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Меню", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU


def send_info_to_flourist(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="ждите и меню....")
    return BOUQUET_MENU


def save_name(update, context):
    client_contacts.append(update.message.text)
    update.message.reply_text('Укажите номер телефона для связи:')
    return SAVE_PHONE


def save_phone(update, context):
    client_contacts.append(update.message.text)
    update.message.reply_text('На какой адрес нужна доставка:')
    return SAVE_ADDRESS


def save_address(update, context):
    client_contacts.append(update.message.text)
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(1, 7)]
    buttons = [[date.strftime("%d.%m.%Y")] for date in dates]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    update.message.reply_text('Выберите дату: ', reply_markup=reply_markup)
    return SAVE_DATE


def save_date(update, context):
    client_contacts.append(update.message.text)
    update.message.reply_text('Желаемое время доставки?')
    return DELIVERY


def send_info_to_courier(update, context):
    client_contacts.append(update.message.text)
    print(client_contacts)


def close(update, context):
    query = update.callback_query
    if query:
        query.edit_message_text(text="Ты это.. заходи, если чё :)")
    else:
        update.message.reply_text('Ты это.. заходи, если чё :)')
    return ConversationHandler.END


def handle_confirm(update, context):
    query = update.callback_query
    query.answer()
    # данные из предыдущего шага
    context.user_data['choice'] = query.data
    print(context.user_data['choice'])


def main():
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            # в начале согласие на обработку персональных данных
            START: [
                CallbackQueryHandler(main_menu, pattern="^agree$"),
                CallbackQueryHandler(close, pattern="^disagree$"),
            ],
            # главное меню
            MAIN_MENU: [
                CallbackQueryHandler(handle_confirm, pattern="^catalog$"),
                CallbackQueryHandler(handle_confirm, pattern="^choose_buqete$"),
                CallbackQueryHandler(handle_confirm, pattern="^consultution$"),
            ],
            # каталог букетов
            CATALOG: [
                CallbackQueryHandler(handle_confirm, pattern="^previous_bouquet$"),
                CallbackQueryHandler(handle_confirm, pattern="^next_bouquet$"),
                CallbackQueryHandler(handle_confirm, pattern="^select_bouquet$"),
            ],
            # выбор события
            EVENT_CHOICE: [
                CallbackQueryHandler(handle_confirm, pattern="^birthday$"),
                CallbackQueryHandler(handle_confirm, pattern="^wedding$"),
                CallbackQueryHandler(handle_confirm, pattern="^school$"),
                CallbackQueryHandler(handle_confirm, pattern="^no_reason$"),
                CallbackQueryHandler(handle_confirm, pattern="^other_occasion$"),
            ],
            # меню при выбранном букете (ещё букет? консультация? в меню?)
            BOUQUET_MENU: [

            ],
            # выбор цвета букета
            COLOR_CHOICE: [

            ],
            # выбор стоимости букета
            PRICE_CHOICE: [

            ],
            # консультация....не додумала... отправка номера телефона для консультации флористу
            CONSULTATION:     [MessageHandler(Filters.text, send_info_to_flourist)],
            # Для оформления заказа: имя
            SAVE_NAME:     [MessageHandler(Filters.text, save_name)],
            # Для оформления заказа: телефон
            SAVE_PHONE:    [MessageHandler(Filters.text, save_phone)],
            # Для оформления заказа: адрес доставки
            SAVE_ADDRESS:  [MessageHandler(Filters.text, save_address)],
            # Для оформления заказа: дата доставки
            SAVE_DATE:     [MessageHandler(Filters.text, save_date)],
            # подтверждение заказа
            ORDER_CONFIRM: [

            ],
            # выбор способа оплаты
            PAYMENT_CHOICE: [
 
            ],
            # отправка информации о заказе курьеру
            DELIVERY:      [MessageHandler(Filters.text, send_info_to_courier)],
        },
        fallbacks=[CommandHandler("close", close)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
