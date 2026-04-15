"""Сценарий консультации NEWGOLD: шаги, ключи данных, сводка для менеджера."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class ConsultStates(StatesGroup):
    """Пошаговое выявление потребностей."""

    occasion = State()
    category = State()
    gold = State()
    stones = State()
    budget = State()
    notes = State()
    review = State()


# Ключи в FSM data
KEY_OCCASION = "occasion"
KEY_CATEGORY = "category"
KEY_GOLD = "gold"
KEY_STONES = "stones"
KEY_BUDGET = "budget"
KEY_NOTES = "notes"

# Человекочитаемые подписи (значение callback → текст)
LABELS: dict[str, dict[str, str]] = {
    KEY_OCCASION: {
        "self": "Для себя",
        "gift": "Подарок",
        "other": "Другое / уточню в комментарии",
    },
    KEY_CATEGORY: {
        "ring": "Кольца",
        "ear": "Серьги",
        "pendant": "Подвески / колье",
        "bracelet": "Браслеты / цепи",
        "other": "Другое",
    },
    KEY_GOLD: {
        "red": "Красное золото",
        "yellow": "Жёлтое золото",
        "white": "Белое золото",
        "unsure": "Нужна помощь с выбором оттенка",
    },
    KEY_STONES: {
        "yes": "Важен подбор камня",
        "no": "Без камня",
        "maybe": "Пока не решила(и)",
    },
    KEY_BUDGET: {
        "b1": "До 50 000 ₽",
        "b2": "50 000 – 150 000 ₽",
        "b3": "От 150 000 ₽",
        "mgr": "Обсудить с менеджером",
    },
}


def label_for(key: str, value: str) -> str:
    return LABELS.get(key, {}).get(value, value)


def format_consult_summary(data: dict) -> str:
    """Текст сводки для пользователя и для заявки менеджеру."""
    lines = [
        "<b>Сводка консультации NEWGOLD</b>",
        "",
        f"• Повод: {label_for(KEY_OCCASION, str(data.get(KEY_OCCASION, '—')))}",
        f"• Категория: {label_for(KEY_CATEGORY, str(data.get(KEY_CATEGORY, '—')))}",
        f"• Золото: {label_for(KEY_GOLD, str(data.get(KEY_GOLD, '—')))}",
        f"• Камни: {label_for(KEY_STONES, str(data.get(KEY_STONES, '—')))}",
        f"• Бюджет: {label_for(KEY_BUDGET, str(data.get(KEY_BUDGET, '—')))}",
    ]
    notes = (data.get(KEY_NOTES) or "").strip()
    if notes:
        lines.extend(["", "<b>Пожелания и комментарий:</b>", notes])
    return "\n".join(lines)
