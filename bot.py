import datetime
import json
import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from dotenv import load_dotenv
from environs import Env
from telegram import ReplyKeyboardMarkup, Update, ChatAction, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, ConversationHandler

from keyboards import get_consent_keyboard, get_main_menu_keyboard, get_occasion_keyboard, \
    get_catalog_keyboard, get_bouquet_menu_keyboard, get_bouquet_card_keyboard, \
    get_color_keyboard, get_price_keyboard

env = Env()
load_dotenv()

BOT_TOKEN = env.str('TG_BOT_TOKEN')
FLOURIST_TG_ID = env.str('FLOURIST_TG_ID')
COURIER_TG_ID = env.str('COURIER_TG_ID')

# состояния диалога
START, MAIN_MENU, CATALOG, EVENT_CHOICE, BOUQUET_MENU, COLOR_CHOICE, PRICE_CHOICE, \
    CONSULTATION, SAVE_NAME, SAVE_PHONE, SAVE_ADDRESS, DELIVERY, SAVE_DATE, \
    ORDER_CONFIRM, PAYMENT_CHOICE, PROMOCODE, PAYMENT = range(17)

client_contacts = []
with open('bouquets.json', 'r', encoding='utf-8') as file:
    bouquets = json.load(file)


# старт - вывод документа для согласия на обработку данных
def start(update, context):
    policy_doc = Path('FlowerShop privacy policy.pdf')
    with open(policy_doc, 'rb') as file:
        update.effective_chat.send_document(document=file,
                                            caption="Подтвердите согласие на обработку персональных данных "
                                            "в соответствии с политикой конфиденциальности.",
                                            reply_markup=get_consent_keyboard())
    return START


# Мини-сервер Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_server():
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    httpd.serve_forever()

# Запускаем сервер в отдельном потоке
threading.Thread(target=run_server, daemon=True).start()


# вывод главного меню
def main_menu(update, context):
    query = update.callback_query
    query.answer()
    update.effective_chat.send_message(text="Меню", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU


def handle_color(update, context):
    query = update.callback_query
    query.answer()
    color = query.data.replace("color_", "")
    context.user_data["color"] = color

    query.edit_message_text(
        text="Выберите бюджет 🌸",
        reply_markup=get_price_keyboard()
    )
    return PRICE_CHOICE

def handle_price(update, context):
    query = update.callback_query
    query.answer()

    # Сохраняем бюджет
    price_data = query.data.replace("price_", "")
    context.user_data["price"] = int(price_data)

    # Загружаем базу (она у тебя уже загружается в начале файла в переменную bouquets)
    # Но для надежности можно прочитать файл здесь или использовать глобальную переменную
    global bouquets 

    occasion = context.user_data.get("occasion")
    color = context.user_data.get("color")
    max_price = context.user_data.get("price")

    # Фильтруем (важно: в JSON ключи теперь на английском!)
    if occasion == "other_occasion":
        suitable = [
            b for b in bouquets 
            if (color == "any" or b['color'] == color) 
            and b['price'] <= max_price
        ]
    else:
        suitable = [
            b for b in bouquets 
            if b['occasion'] == occasion 
            and (color == "any" or b['color'] == color) 
            and b['price'] <= max_price
        ]

    if not suitable:
        suitable = [b for b in bouquets if b['occasion'] == occasion]

    if suitable:
        selected = random.choice(suitable)
        caption = (
            f"💐 {selected['name']}\n\n"
            f"✨ Смысл: {selected['meaning']}\n"
            f"🌿 Состав: {', '.join(selected['composition'])}\n\n"
            f"💰 Цена: {selected['price']} руб."
        )

        query.message.delete()
        
        try:
            with open(selected['image'], 'rb') as photo:
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=get_bouquet_card_keyboard(selected['id'])
                )
        except Exception:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🖼 (Фото не найдено)\n\n{caption}",
                reply_markup=get_bouquet_card_keyboard(selected['id'])
            )
    else:
        query.edit_message_text("Ничего не нашлось, попробуйте изменить параметры.")

    return BOUQUET_MENU

# вывод каталога (один букет и кнопки навигации)
def show_catalog(update, context):
    query = update.callback_query
    if 'cur_bouquet' not in context.user_data:
        context.user_data['cur_bouquet'] = 0
    bouquet_id = context.user_data['cur_bouquet']
    bouquet = bouquets[bouquet_id]
    bouquet_photo = bouquet['image']
    if query:
        query.answer()
        if query.data == "next_bouquet" or query.data == "previous_bouquet":
            with open(bouquet_photo, 'rb') as file:
                query.edit_message_media(
                    media=InputMediaPhoto(file, caption=f"{bouquet['meaning']}\n{bouquet['price']} руб."),
                    reply_markup=get_catalog_keyboard())
            return CATALOG
    update.effective_chat.send_chat_action(action=ChatAction.UPLOAD_PHOTO)
    with open(bouquet_photo, 'rb') as file:
        update.effective_chat.send_photo(photo=file,
                                         caption=f"{bouquet['meaning']}\n{bouquet['price']} руб.",
                                         reply_markup=get_catalog_keyboard())
    return CATALOG


# навигация по каталогу - след.букет
def get_next_bouquet(update, context):
    if 'cur_bouquet' in context.user_data:
        if context.user_data['cur_bouquet'] < len(bouquets) - 1:
            context.user_data['cur_bouquet'] += 1
            return show_catalog(update, context)
    return CATALOG


# навигация по каталогу - пред.букет
def get_prev_bouquet(update, context):
    if 'cur_bouquet' in context.user_data:
        if context.user_data['cur_bouquet'] > 0:
            context.user_data['cur_bouquet'] -= 1
            return show_catalog(update, context)
    return CATALOG


# вывод выбранного букета и меню для дальнейших действий
def show_bouquet_menu(update, context):
    query = update.callback_query
    query.answer()
    bouquet_id = context.user_data['cur_bouquet']
    bouquet = bouquets[bouquet_id]
    bouquet_photo = bouquet['image']
    with open(bouquet_photo, 'rb') as file:
        query.edit_message_media(media=InputMediaPhoto(file, caption=f"{bouquet['meaning']}\n"
                                 f"{', '.join(bouquet['composition'])}\n{bouquet['price']} руб."),
                                 reply_markup=get_bouquet_menu_keyboard())
    return BOUQUET_MENU


# начало оформления заказа, запрос имени
def start_order(update, context):
    query = update.callback_query
    
    if query:
        query.answer()
        # Если в data есть ID (например, "order_5"), вытаскиваем его
        if "_" in query.data:
            bouquet_id = query.data.split("_")[1]
            # Сохраняем ID конкретного букета из кнопки
            context.user_data['order_bouquet_id'] = bouquet_id
        else:
            # Если нажали "Заказать" в обычном меню, берем текущий просматриваемый
            current_idx = context.user_data.get('cur_bouquet', 0)
            context.user_data['order_bouquet_id'] = bouquets[current_idx]['id']

    update.effective_chat.send_message('Для оформления заказа укажите Ваше имя:')
    return SAVE_NAME


# выбор событий для выбора
def show_events(update, context):
    print("Вывод событий на выбор")
    query = update.callback_query
    query.answer()
    update.effective_chat.send_message(text="К какому событию готовимся? "
                                       "Выберите один из вариантов, либо укажите свой",
                                       reply_markup=get_occasion_keyboard())
    return EVENT_CHOICE


# запрос телефона для консультации
def request_consultation(update, context):
    update.effective_chat.send_message('Введите номер телефона и флорист перезвонит Вам в течение 20 минут:')
    return CONSULTATION


# отправка телефона флористу для перезвона, переход к каталогу
def send_info_to_flourist(update, context):
    context.bot.send_message(chat_id=FLOURIST_TG_ID, text=f"Запрос консультации.\nТелефон: {update.message.text}")
    update.effective_chat.send_message(text="Флорист скоро свяжется с Вами, "
                                       "а пока можете присмотреть что-нибудь из готовой коллекции")
    show_catalog(update, context)
    return CATALOG


# сохранение имени, запрос телефона для доставки
def save_name(update, context):
    context.user_data['order_name'] = update.message.text
    update.effective_chat.send_message('Укажите номер телефона для связи:')
    return SAVE_PHONE


# сохранение телефона, запрос ПРОМОКОДА
def save_phone(update, context):
    context.user_data['order_phone'] = update.message.text
    update.message.reply_text('Введите промокод (если есть) или напишите "нет":')
    return PROMOCODE # Теперь идем сюда

# Обработка промокода
def handle_promocode(update, context):
    user_text = update.message.text.upper().strip()
    if user_text == "FLOWER2026":
        context.user_data['discount'] = "10%"
        update.message.reply_text("🎉 Промокод применен! Скидка 10%")
    else:
        context.user_data['discount'] = "0%"
        if user_text.lower() != "нет":
            update.message.reply_text("Промокод не найден, продолжаем без скидки.")
    
    update.message.reply_text('На какой адрес нужна доставка:')
    return SAVE_ADDRESS


# сохранение адреса, запрос даты доставки
def save_address(update, context):
    context.user_data['order_address'] = update.message.text 
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(1, 7)]
    buttons = [[date.strftime("%d.%m.%Y")] for date in dates]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    update.message.reply_text('Выберите дату: ', reply_markup=reply_markup)
    return SAVE_DATE


# сохранение даты, запрос времени для доставки И запрос оплаты
def save_date(update, context):
    context.user_data['order_date'] = update.message.text
    update.message.reply_text('Желаемое время доставки:')
    return PAYMENT


# Запрос оплаты после ввода всех данных
def request_payment(update, context):
    # Достаем цену выбранного букета (учитывая скидку, если хочешь заморочиться)
    # Для простоты напишем общую инструкцию
    text = (
        "💳 Для оплаты переведите сумму заказа по номеру +79991234567 (СБП, Банк Т).\n"
        "После перевода, пожалуйста, **пришлите скриншот чека** прямо сюда в чат.\n\n"
        "Как только мы получим подтверждение, заказ будет передан курьеру!"
    )
    update.message.reply_text(text)
    return PAYMENT

# Ловим скриншот чека
def handle_payment_screenshot(update, context):
    # ШАГ 1: Если время еще не введено, значит текущее сообщение — это время доставки
    if 'order_time' not in context.user_data:
        context.user_data['order_time'] = update.message.text
        
        # Теперь, когда время сохранено, просим оплату
        text = (
            "💳 Для оплаты переведите сумму заказа по номеру +79991234567.\n"
            "После перевода **пришлите скриншот чека** сюда в чат."
        )
        update.message.reply_text(text)
        return PAYMENT # Остаемся в этом же состоянии, ждем фото

    # ШАГ 2: Если время уже есть, проверяем, прислал ли пользователь фото
    if update.message.photo:
        context.user_data['payment_screenshot'] = update.message.photo[-1].file_id
        update.message.reply_text("✅ Чек получен! Данные переданы курьеру.")
        return send_info_to_courier(update, context)
    
    # Если прислали текст вместо фото на этапе оплаты
    update.message.reply_text("Пожалуйста, пришлите скриншот чека (фотографией).")
    return PAYMENT

# отправка инфы заказа курьеру
def send_info_to_courier(update, context):
    # Берем данные ТОЛЬКО из context.user_data
    b_id = context.user_data.get('order_bouquet_id', 'Неизвестно')
    discount = context.user_data.get('discount', '0%')
    name = context.user_data.get('order_name', 'Не указано')
    phone = context.user_data.get('order_phone', 'Не указано')
    address = context.user_data.get('order_address', 'Не указано')
    date = context.user_data.get('order_date', 'Не указано')
    time = context.user_data.get('order_time', 'Не указано') # Теперь тут будет время, а не "None"

    order_details = (
        f"🚀 НОВЫЙ ЗАКАЗ!\n"
        f"💐 ID букета: {b_id}\n"
        f"💰 Скидка: {discount}\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Адрес: {address}\n"
        f"Дата: {date}\n"
        f"Время: {time}"
    )
    
    context.bot.send_message(chat_id=COURIER_TG_ID, text=order_details)
    
    screenshot = context.user_data.get('payment_screenshot')
    if screenshot:
        context.bot.send_photo(chat_id=COURIER_TG_ID, photo=screenshot, caption="🧾 Чек об оплате")
    
    update.message.reply_text("Спасибо! Ваш заказ принят! 🌸")
    return ConversationHandler.END


# обработка закрытия диалога
def close(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Пока! Ты это.. заходи, если чё :)")
    return ConversationHandler.END


# пример какой-то
def handle_occasion(update, context):
    query = update.callback_query
    query.answer()
    
    # Сохраняем повод
    context.user_data["occasion"] = query.data
    
    # Спрашиваем про цвет
    query.edit_message_text(
        text="Предпочитаете какую-то цветовую гамму? 🎨",
        reply_markup=get_color_keyboard()
    )
    return COLOR_CHOICE


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
                CallbackQueryHandler(show_catalog, pattern="^catalog$"),
                CallbackQueryHandler(show_events, pattern="^choose_buqete$"),
                CallbackQueryHandler(request_consultation, pattern="^consultution$"),
            ],
            # каталог букетов
            CATALOG: [
                CallbackQueryHandler(get_prev_bouquet, pattern="^previous_bouquet$"),
                CallbackQueryHandler(get_next_bouquet, pattern="^next_bouquet$"),
                CallbackQueryHandler(show_bouquet_menu, pattern="^select_bouquet$"),
            ],
            # выбор события
            EVENT_CHOICE: [
                CallbackQueryHandler(handle_occasion, pattern="^birthday$"),
                CallbackQueryHandler(handle_occasion, pattern="^wedding$"),
                CallbackQueryHandler(handle_occasion, pattern="^school$"),
                CallbackQueryHandler(handle_occasion, pattern="^no_reason$"),
                CallbackQueryHandler(handle_occasion, pattern="^other_occasion$"),
            ],
            # меню при выбранном букете (ещё букет? консультация? в меню?)
            BOUQUET_MENU: [
                CallbackQueryHandler(start_order, pattern="^order"),
                CallbackQueryHandler(show_catalog, pattern="^catalog$"),
                CallbackQueryHandler(main_menu, pattern="^main_menu$"),
                # Добавляем обработку кнопки консультации, если она есть в клавиатуре букета
                CallbackQueryHandler(request_consultation, pattern="^consultution$"),
                # Если пользователь просто напишет текст, пока открыт букет:
                MessageHandler(Filters.text & ~Filters.command, request_consultation),
            ],
            # выбор цвета букета
            COLOR_CHOICE: [
                CallbackQueryHandler(handle_color, pattern="^color_")
            ],
            # выбор стоимости букета
            PRICE_CHOICE: [
                CallbackQueryHandler(handle_price, pattern="^price_")
            ],
            # консультация....не додумала... отправка номера телефона для консультации флористу
            CONSULTATION:     [MessageHandler(Filters.text, send_info_to_flourist)],
            # Для оформления заказа: имя
            SAVE_NAME:     [MessageHandler(Filters.text, save_name)],
            # Для оформления заказа: телефон
            SAVE_PHONE:    [MessageHandler(Filters.text, save_phone)],
            # Обработка промокода
            PROMOCODE:     [MessageHandler(Filters.text, handle_promocode)],
            # Для оформления заказа: адрес доставки
            SAVE_ADDRESS:  [MessageHandler(Filters.text, save_address)],
            # Для оформления заказа: дата доставки
            SAVE_DATE:     [MessageHandler(Filters.text, save_date)],
            # выбор способа оплаты
            PAYMENT: [MessageHandler(Filters.photo, handle_payment_screenshot),
                      MessageHandler(Filters.text & ~Filters.command, handle_payment_screenshot)],
            # подтверждение заказа
            ORDER_CONFIRM: [

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
