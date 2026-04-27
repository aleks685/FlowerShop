from keyboards import (
    get_occasion_keyboard,
    get_color_keyboard,
    get_price_keyboard,
    get_bouquet_menu_keyboard,
)


MAIN_MENU = 1
EVENT_CHOICE = 3
BOUQUET_MENU = 4
COLOR_CHOICE = 5
PRICE_CHOICE = 6


def show_events(update, context):
    query = update.callback_query
    query.answer()

    update.effective_chat.send_message(
        text="К какому событию готовимся? 🌸",
        reply_markup=get_occasion_keyboard()
    )

    return EVENT_CHOICE


def save_occasion(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["occasion"] = query.data

    update.effective_chat.send_message(
        text="Выберите цветовую гамму 🌸",
        reply_markup=get_color_keyboard()
    )

    return COLOR_CHOICE


def save_color(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["color"] = query.data

    update.effective_chat.send_message(
        text="Выберите бюджет 💰",
        reply_markup=get_price_keyboard()
    )

    return PRICE_CHOICE


def save_price(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["price"] = int(query.data)

    occasion = context.user_data["occasion"]
    color = context.user_data["color"]
    price = context.user_data["price"]

    bouquets = context.bot_data["bouquets"]

    matched_bouquets = []

    for bouquet in bouquets:
        if (
            bouquet["occasion"] == occasion
            and bouquet["color"] == color
            and bouquet["price"] == price
        ):
            matched_bouquets.append(bouquet)

    if not matched_bouquets:
        update.effective_chat.send_message(
            text="К сожалению, подходящих букетов пока нет 🌸"
        )
        return MAIN_MENU

    bouquet = matched_bouquets[0]

    context.user_data["cur_bouquet"] = bouquets.index(bouquet)

    bouquet_photo = f'images/id{bouquet["id"]}.jpg'

    with open(bouquet_photo, "rb") as file:
        update.effective_chat.send_photo(
            photo=file,
            caption=(
                f"🌸 {bouquet['name']}\n\n"
                f"{bouquet['meaning']}\n"
                f"Состав: {', '.join(bouquet['composition'])}\n"
                f"Цена: {bouquet['price']} руб."
            ),
            reply_markup=get_bouquet_menu_keyboard()
        )

    return BOUQUET_MENU