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
                                 callback_data="choose_bouquet"),
            InlineKeyboardButton(
                "[👩‍🎨 Консультация флориста]", callback_data="consultation")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_occasion_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🎂 День рождения",
                callback_data="occasion_birthday"
            ),
            InlineKeyboardButton(
                "💍 Свадьба",
                callback_data="occasion_wedding"
            )
        ],
        [
            InlineKeyboardButton(
                "🏫 В школу",
                callback_data="occasion_school"
            ),
            InlineKeyboardButton(
                "🌷 Без повода",
                callback_data="occasion_other"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ Другой повод",
                callback_data="occasion_no_reason"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_color_keyboard():
    keyboard = [
        [InlineKeyboardButton("🤍 Светлый", callback_data="color_light")],
        [InlineKeyboardButton("🌈 Яркий", callback_data="color_bright")],
        [InlineKeyboardButton("🌸 Мягкий", callback_data="color_soft")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_price_keyboard():
    keyboard = [
        [InlineKeyboardButton("500 ₽", callback_data="price_500")],
        [InlineKeyboardButton("1000 ₽", callback_data="price_1000")],
        [InlineKeyboardButton("2000 ₽", callback_data="price_2000")],
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
