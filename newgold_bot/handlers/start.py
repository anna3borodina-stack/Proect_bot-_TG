import html

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from newgold_bot import texts
from newgold_bot.keyboards import main_menu_reply
from newgold_bot.state import get_app_settings
from newgold_bot.storage import set_consent

router = Router(name="start")


def _privacy_keyboard(privacy_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Открыть политику", url=privacy_url)],
            [
                InlineKeyboardButton(text="✅ Согласен(на)", callback_data="consent:yes"),
                InlineKeyboardButton(text="❌ Не согласен(на)", callback_data="consent:no"),
            ],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    settings = get_app_settings()
    if not settings.privacy_policy_url:
        await message.answer(texts.MSG_PRIVACY_NOT_CONFIGURED)
        return

    await message.answer(
        texts.start_welcome(settings.store_url or None, settings.bot_public_url or None),
        reply_markup=_privacy_keyboard(settings.privacy_policy_url),
    )


@router.callback_query(F.data == "consent:yes")
async def consent_yes(callback: CallbackQuery) -> None:
    if callback.from_user:
        set_consent(callback.from_user.id, True)
    await callback.answer()
    if callback.message:
        settings = get_app_settings()
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            texts.after_consent(settings.store_url or None, settings.bot_public_url or None),
            reply_markup=main_menu_reply(),
        )


@router.callback_query(F.data == "consent:no")
async def consent_no(callback: CallbackQuery) -> None:
    if callback.from_user:
        set_consent(callback.from_user.id, False)
    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(texts.MSG_CONSENT_DECLINED)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    settings = get_app_settings()
    await message.answer(
        texts.help_message(settings.bot_public_url or None),
        parse_mode="HTML",
    )


@router.message(Command("chatid"))
async def cmd_chatid(message: Message) -> None:
    """Показать ID текущего чата — для заполнения MANAGER_CHAT_ID в группе менеджеров."""
    cid = message.chat.id
    ctype = message.chat.type
    title = message.chat.title
    parts = [
        "<b>ID этого чата</b> (вставьте в <code>MANAGER_CHAT_ID</code> в <code>.env</code>):",
        f"<code>{cid}</code>",
        f"Тип: <code>{ctype}</code>",
    ]
    if title:
        parts.append(f"Название: {html.escape(title)}")
    if ctype == "private":
        parts.append("")
        parts.append(
            "Это личный чат с ботом. Чтобы получить ID <b>группы</b> менеджеров: "
            "добавьте бота в группу и отправьте <code>/chatid</code> уже <b>в группе</b>."
        )
    else:
        parts.append("")
        parts.append("Скопируйте число (с минусом, если есть) в MANAGER_CHAT_ID и перезапустите бота.")
    await message.answer("\n".join(parts), parse_mode="HTML")
