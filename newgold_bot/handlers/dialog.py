"""Сценарий консультации, статические разделы, заявка менеджеру — без внешних API."""

from __future__ import annotations

import html
import logging
from typing import Any

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User

from newgold_bot import texts
from newgold_bot.keyboards import (
    consult_budget_kb,
    consult_category_kb,
    consult_gold_kb,
    consult_notes_kb,
    consult_occasion_kb,
    consult_review_kb,
    consult_stones_kb,
    main_menu_reply,
)
from newgold_bot.scenario import (
    KEY_BUDGET,
    KEY_CATEGORY,
    KEY_GOLD,
    KEY_NOTES,
    KEY_OCCASION,
    KEY_STONES,
    ConsultStates,
    format_consult_summary,
)
from newgold_bot.state import get_app_settings
from newgold_bot.storage import has_consent

logger = logging.getLogger(__name__)

router = Router(name="dialog")


class ManagerStates(StatesGroup):
    waiting_details = State()


def _drop_downstream(data: dict[str, Any], keep_through: str) -> dict[str, Any]:
    order = [KEY_OCCASION, KEY_CATEGORY, KEY_GOLD, KEY_STONES, KEY_BUDGET, KEY_NOTES]
    i = order.index(keep_through)
    drop = set(order[i + 1 :])
    return {k: v for k, v in data.items() if k not in drop}


def _format_manager_notice(user: User | None, details: str) -> str:
    uid = user.id if user else "—"
    uname = user.username if user and user.username else "—"
    name = user.full_name if user else "—"
    safe_name = html.escape(name)
    safe_uname = html.escape(uname)
    safe_details = html.escape(details)
    return (
        "🔔 <b>Заявка NEWGOLD</b>\n"
        f"Пользователь: <code>{uid}</code>\n"
        f"Имя: {safe_name}\n"
        f"@{safe_uname}\n"
        "—\n"
        f"{safe_details}"
    )


def _format_manager_consult_html(user: User | None, data: dict[str, Any]) -> str:
    plain = format_consult_summary(data)
    # Сводка уже с HTML-тегами из format_consult_summary
    uid = user.id if user else "—"
    uname = user.username if user and user.username else "—"
    name = user.full_name if user else "—"
    safe_name = html.escape(name)
    safe_uname = html.escape(uname)
    return (
        "🔔 <b>Заявка NEWGOLD — после консультации</b>\n"
        f"Пользователь: <code>{uid}</code>\n"
        f"Имя: {safe_name}\n"
        f"@{safe_uname}\n"
        "—\n"
        f"{plain}"
    )


async def _send_to_manager_chat(bot, chat_id: int, text: str) -> bool:
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return True
    except Exception as e:
        logger.exception("Send to manager chat: %s", e)
        return False


async def open_manager_lead(message: Message, state: FSMContext) -> None:
    """Заявка менеджеру: выходим из консультации и ждём текст."""
    if not message.from_user or not has_consent(message.from_user.id):
        await message.answer(texts.MSG_NEED_PRIVACY_FIRST)
        return
    cur = await state.get_state()
    if cur == ManagerStates.waiting_details.state:
        await message.answer(
            "Вы уже отправляете заявку — напишите одним сообщением текст для менеджера."
        )
        return
    settings = get_app_settings()
    if not settings.manager_chat_id:
        await message.answer(texts.MSG_MANAGER_CHAT_NOT_SET)
        return
    if cur is not None:
        await state.clear()
    await state.set_state(ManagerStates.waiting_details)
    await message.answer(texts.MSG_MANAGER_ASK_DETAILS)


# --- Консультация: старт и кнопки меню ---


@router.message(F.chat.type == ChatType.PRIVATE, F.text == texts.BTN_CONSULT)
async def menu_start_consult(message: Message, state: FSMContext) -> None:
    if not message.from_user or not has_consent(message.from_user.id):
        await message.answer(texts.MSG_NEED_PRIVACY_FIRST)
        return
    await state.clear()
    await state.set_state(ConsultStates.occasion)
    await message.answer(
        texts.MSG_CONSULT_INTRO,
        parse_mode="HTML",
        reply_markup=consult_occasion_kb(),
    )


@router.message(F.chat.type == ChatType.PRIVATE, F.text == texts.BTN_ORDER)
async def menu_order(message: Message) -> None:
    if not message.from_user or not has_consent(message.from_user.id):
        await message.answer(texts.MSG_NEED_PRIVACY_FIRST)
        return
    await message.answer(texts.MSG_ORDER_INFO, parse_mode="HTML", reply_markup=main_menu_reply())


@router.message(F.chat.type == ChatType.PRIVATE, F.text == texts.BTN_STONES_GOLD)
async def menu_stones_gold(message: Message) -> None:
    if not message.from_user or not has_consent(message.from_user.id):
        await message.answer(texts.MSG_NEED_PRIVACY_FIRST)
        return
    await message.answer(texts.MSG_STONES_GOLD_INFO, parse_mode="HTML", reply_markup=main_menu_reply())


# --- Callbacks консультации ---


@router.callback_query(F.data == "cons:cancel", StateFilter(ConsultStates))
async def consult_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(texts.MSG_CANCEL_CONSULT, reply_markup=main_menu_reply())


@router.callback_query(F.data.startswith("cons:occ:"), StateFilter(ConsultStates.occasion))
async def consult_occasion_pick(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user:
        await callback.answer()
        return
    part = callback.data.removeprefix("cons:occ:")
    if part not in ("self", "gift", "other"):
        await callback.answer()
        return
    await state.update_data(**{KEY_OCCASION: part})
    await state.set_state(ConsultStates.category)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_CONSULT_CATEGORY,
            parse_mode="HTML",
            reply_markup=consult_category_kb(),
        )


@router.callback_query(F.data.startswith("cons:cat:"), StateFilter(ConsultStates.category))
async def consult_category_pick(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user:
        await callback.answer()
        return
    part = callback.data.removeprefix("cons:cat:")
    if part not in ("ring", "ear", "pendant", "bracelet", "other"):
        await callback.answer()
        return
    await state.update_data(**{KEY_CATEGORY: part})
    await state.set_state(ConsultStates.gold)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_CONSULT_GOLD,
            parse_mode="HTML",
            reply_markup=consult_gold_kb(),
        )


@router.callback_query(F.data.startswith("cons:gold:"), StateFilter(ConsultStates.gold))
async def consult_gold_pick(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        await callback.answer()
        return
    part = callback.data.removeprefix("cons:gold:")
    if part not in ("red", "yellow", "white", "unsure"):
        await callback.answer()
        return
    await state.update_data(**{KEY_GOLD: part})
    await state.set_state(ConsultStates.stones)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_CONSULT_STONES,
            parse_mode="HTML",
            reply_markup=consult_stones_kb(),
        )


@router.callback_query(F.data.startswith("cons:st:"), StateFilter(ConsultStates.stones))
async def consult_stones_pick(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        await callback.answer()
        return
    part = callback.data.removeprefix("cons:st:")
    if part not in ("yes", "no", "maybe"):
        await callback.answer()
        return
    await state.update_data(**{KEY_STONES: part})
    await state.set_state(ConsultStates.budget)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_CONSULT_BUDGET,
            parse_mode="HTML",
            reply_markup=consult_budget_kb(),
        )


@router.callback_query(F.data.startswith("cons:bd:"), StateFilter(ConsultStates.budget))
async def consult_budget_pick(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        await callback.answer()
        return
    part = callback.data.removeprefix("cons:bd:")
    if part not in ("b1", "b2", "b3", "mgr"):
        await callback.answer()
        return
    await state.update_data(**{KEY_BUDGET: part})
    await state.set_state(ConsultStates.notes)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_CONSULT_NOTES,
            parse_mode="HTML",
            reply_markup=consult_notes_kb(),
        )


@router.callback_query(F.data == "cons:notes:skip", StateFilter(ConsultStates.notes))
async def consult_notes_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(**{KEY_NOTES: ""})
    await state.set_state(ConsultStates.review)
    data = await state.get_data()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_REVIEW_HEADER,
            parse_mode="HTML",
        )
        await callback.message.answer(
            format_consult_summary(data),
            parse_mode="HTML",
            reply_markup=consult_review_kb(),
        )


@router.callback_query(F.data.startswith("cons:back:"), StateFilter(ConsultStates))
async def consult_back(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        await callback.answer()
        return
    step = callback.data.removeprefix("cons:back:")
    data = await state.get_data()
    mapping = {
        "occasion": (ConsultStates.occasion, KEY_OCCASION, texts.MSG_CONSULT_INTRO, consult_occasion_kb),
        "category": (ConsultStates.category, KEY_CATEGORY, texts.MSG_CONSULT_CATEGORY, consult_category_kb),
        "gold": (ConsultStates.gold, KEY_GOLD, texts.MSG_CONSULT_GOLD, consult_gold_kb),
        "stones": (ConsultStates.stones, KEY_STONES, texts.MSG_CONSULT_STONES, consult_stones_kb),
        "budget": (ConsultStates.budget, KEY_BUDGET, texts.MSG_CONSULT_BUDGET, consult_budget_kb),
    }
    if step not in mapping:
        await callback.answer()
        return
    new_state, keep_key, msg_text, kb_fn = mapping[step]
    trimmed = _drop_downstream(data, keep_key)
    await state.set_data(trimmed)
    await state.set_state(new_state)
    await callback.answer("Назад")
    if callback.message:
        await callback.message.answer(msg_text, parse_mode="HTML", reply_markup=kb_fn())


@router.callback_query(F.data == "cons:review:send", StateFilter(ConsultStates.review))
async def consult_review_send(callback: CallbackQuery, state: FSMContext) -> None:
    settings = get_app_settings()
    chat_id = settings.manager_chat_id
    if not chat_id:
        await callback.answer("Чат менеджеров не настроен.", show_alert=True)
        return
    data = await state.get_data()
    body = _format_manager_consult_html(callback.from_user, data)
    ok = await _send_to_manager_chat(callback.bot, chat_id, body)
    await callback.answer()
    await state.clear()
    if callback.message:
        if ok:
            await callback.message.answer(texts.MSG_MANAGER_SENT, reply_markup=main_menu_reply())
        else:
            await callback.message.answer(texts.MSG_MANAGER_SEND_FAILED, reply_markup=main_menu_reply())


@router.callback_query(F.data == "cons:review:again", StateFilter(ConsultStates.review))
async def consult_review_again(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ConsultStates.occasion)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            texts.MSG_CONSULT_INTRO,
            parse_mode="HTML",
            reply_markup=consult_occasion_kb(),
        )


@router.callback_query(F.data == "cons:review:home", StateFilter(ConsultStates.review))
async def consult_review_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Главное меню. Выберите раздел:",
            reply_markup=main_menu_reply(),
        )


# --- Заметки (текст) ---


@router.message(StateFilter(ConsultStates.notes), F.text)
async def consult_notes_text(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if not raw:
        await message.answer(texts.MSG_CONSULT_NOTES_EMPTY)
        return
    await state.update_data(**{KEY_NOTES: raw})
    await state.set_state(ConsultStates.review)
    data = await state.get_data()
    await message.answer(texts.MSG_REVIEW_HEADER, parse_mode="HTML")
    await message.answer(
        format_consult_summary(data),
        parse_mode="HTML",
        reply_markup=consult_review_kb(),
    )


@router.message(StateFilter(ConsultStates.notes))
async def consult_notes_bad(message: Message) -> None:
    await message.answer(texts.MSG_CONSULT_NOTES_NON_TEXT)


@router.message(StateFilter(ConsultStates.review), F.text)
async def consult_review_text(message: Message) -> None:
    await message.answer(texts.MSG_REVIEW_USE_BUTTONS)


# --- Не текст в шагах с кнопками ---


@router.message(
    StateFilter(
        ConsultStates.occasion,
        ConsultStates.category,
        ConsultStates.gold,
        ConsultStates.stones,
        ConsultStates.budget,
    ),
    F.text,
)
async def consult_use_buttons(message: Message) -> None:
    await message.answer(texts.MSG_CONSULT_USE_BUTTONS)


# --- Команды ---


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    cur = await state.get_state()
    if cur is None:
        await message.answer("Сейчас нет активного сценария. Справка: /help")
        return
    await state.clear()
    await message.answer(texts.MSG_CANCEL_CONSULT, reply_markup=main_menu_reply())


@router.message(Command("clear"))
async def cmd_clear(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.MSG_CLEAR_DONE, reply_markup=main_menu_reply())


@router.message(Command("manager"))
async def cmd_manager(message: Message, state: FSMContext) -> None:
    await open_manager_lead(message, state)


@router.message(StateFilter(ManagerStates.waiting_details), F.text)
async def manager_details(message: Message, state: FSMContext) -> None:
    if message.text and message.text.strip() == texts.BTN_MANAGER:
        await message.answer("Напишите, пожалуйста, обычным текстом, чем мы можем помочь — не кнопкой.")
        return
    settings = get_app_settings()
    chat_id = settings.manager_chat_id
    if not chat_id:
        await state.clear()
        await message.answer(texts.MSG_MANAGER_CHAT_MISSING)
        return
    details = (message.text or "").strip()
    if not details:
        await message.answer(texts.MSG_MANAGER_EMPTY)
        return
    text = _format_manager_notice(message.from_user, details)
    ok = await _send_to_manager_chat(message.bot, chat_id, text)
    await state.clear()
    if ok:
        await message.answer(texts.MSG_MANAGER_SENT, reply_markup=main_menu_reply())
    else:
        await message.answer(texts.MSG_MANAGER_SEND_FAILED, reply_markup=main_menu_reply())


@router.message(StateFilter(ManagerStates.waiting_details))
async def manager_need_text(message: Message) -> None:
    await message.answer(texts.MSG_MANAGER_NEED_TEXT)


@router.message(F.chat.type == ChatType.PRIVATE, F.text == texts.BTN_MANAGER)
async def btn_manager(message: Message, state: FSMContext) -> None:
    await open_manager_lead(message, state)


@router.message(F.chat.type == ChatType.PRIVATE, F.text)
async def fallback_private_text(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    if not has_consent(message.from_user.id):
        await message.answer(texts.MSG_NEED_PRIVACY_CHAT)
        return
    st = await state.get_state()
    if st is not None:
        return
    await message.answer(
        "Выберите, пожалуйста, раздел в меню ниже или нажмите 🎯 Консультация. "
        "Справка: /help",
        reply_markup=main_menu_reply(),
    )
