from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_consent_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✅ Согласен", callback_data="agree"),
            InlineKeyboardButton("❌ Не согласен", callback_data="disagree"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("[ 📚 Каталог ]", callback_data="catalog"),
            InlineKeyboardButton("[💐 Подобрать букет]",
                                 callback_data="choose_buqete"),
            InlineKeyboardButton(
                "[👩‍🎨 Консультация флориста]", callback_data="consultution")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_occasion_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🎂 День рождения",
                callback_data="birthday"
            ),
            InlineKeyboardButton(
                "💍 Свадьба",
                callback_data="wedding"
            )
        ],
        [
            InlineKeyboardButton(
                "🏫 В школу",
                callback_data="school"
            ),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_catalog_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ Предыдущий",
                callback_data="previous_bouquet"
            ),
            InlineKeyboardButton(
                "➡️ Следующий",
                callback_data="next_bouquet"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Выбрать букет",
                callback_data="select_bouquet"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_bouquet_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("[ 💐 оформить заказ ]", callback_data="order"),
            InlineKeyboardButton("[📚 назад к каталогу]",
                                 callback_data="catalog"),
            InlineKeyboardButton(
                "[ вернуться в меню]", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_color_keyboard():
    keyboard = [
        [InlineKeyboardButton("🤍 Светлый", callback_data="light")],
        [InlineKeyboardButton("🌈 Яркий", callback_data="bright")],
        [InlineKeyboardButton("🌸 Мягкий", callback_data="soft")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_price_keyboard():
    keyboard = [
        [InlineKeyboardButton("500 ₽", callback_data="500")],
        [InlineKeyboardButton("1000 ₽", callback_data="1000")],
        [InlineKeyboardButton("2000 ₽", callback_data="2000")],
    ]

    return InlineKeyboardMarkup(keyboard)
