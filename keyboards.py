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
            InlineKeyboardButton(
                "🌷 Без повода",
                callback_data="no_reason"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ Другой повод",
                callback_data="other_occasion"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
