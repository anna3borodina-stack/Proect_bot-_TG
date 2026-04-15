"""Клавиатуры: главное меню и шаги консультации."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from newgold_bot import texts


def main_menu_reply() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=texts.BTN_CONSULT),
                KeyboardButton(text=texts.BTN_ORDER),
            ],
            [
                KeyboardButton(text=texts.BTN_STONES_GOLD),
                KeyboardButton(text=texts.BTN_MANAGER),
            ],
            [KeyboardButton(text=texts.BTN_SITE)],
        ],
        resize_keyboard=True,
    )


def site_url_inline(url: str) -> InlineKeyboardMarkup:
    """Кнопка-ссылка на витрину (url должен быть с http/https)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Перейти на сайт NEWGOLD", url=url)],
        ]
    )


def consult_occasion_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Для себя", callback_data="cons:occ:self"),
                InlineKeyboardButton(text="Подарок", callback_data="cons:occ:gift"),
            ],
            [InlineKeyboardButton(text="Другое — уточню в комментарии", callback_data="cons:occ:other")],
            [InlineKeyboardButton(text="« Отмена", callback_data="cons:cancel")],
        ]
    )


def consult_category_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Кольца", callback_data="cons:cat:ring"),
                InlineKeyboardButton(text="Серьги", callback_data="cons:cat:ear"),
            ],
            [
                InlineKeyboardButton(text="Подвески / колье", callback_data="cons:cat:pendant"),
                InlineKeyboardButton(text="Браслеты / цепи", callback_data="cons:cat:bracelet"),
            ],
            [InlineKeyboardButton(text="Другое", callback_data="cons:cat:other")],
            [InlineKeyboardButton(text="« Назад", callback_data="cons:back:occasion")],
        ]
    )


def consult_gold_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Красное", callback_data="cons:gold:red"),
                InlineKeyboardButton(text="Жёлтое", callback_data="cons:gold:yellow"),
                InlineKeyboardButton(text="Белое", callback_data="cons:gold:white"),
            ],
            [InlineKeyboardButton(text="Нужна помощь с оттенком", callback_data="cons:gold:unsure")],
            [InlineKeyboardButton(text="« Назад", callback_data="cons:back:category")],
        ]
    )


def consult_stones_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подбор камня важен", callback_data="cons:st:yes"),
                InlineKeyboardButton(text="Без камня", callback_data="cons:st:no"),
            ],
            [InlineKeyboardButton(text="Пока не решила(и)", callback_data="cons:st:maybe")],
            [InlineKeyboardButton(text="« Назад", callback_data="cons:back:gold")],
        ]
    )


def consult_budget_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="До 50 000 ₽", callback_data="cons:bd:b1"),
                InlineKeyboardButton(text="50–150 тыс. ₽", callback_data="cons:bd:b2"),
            ],
            [
                InlineKeyboardButton(text="От 150 000 ₽", callback_data="cons:bd:b3"),
                InlineKeyboardButton(text="С менеджером", callback_data="cons:bd:mgr"),
            ],
            [InlineKeyboardButton(text="« Назад", callback_data="cons:back:stones")],
        ]
    )


def consult_notes_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="cons:notes:skip")],
            [InlineKeyboardButton(text="« Назад", callback_data="cons:back:budget")],
        ]
    )


def consult_review_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить менеджеру", callback_data="cons:review:send")],
            [
                InlineKeyboardButton(text="🔄 Пройти заново", callback_data="cons:review:again"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="cons:review:home"),
            ],
        ]
    )
