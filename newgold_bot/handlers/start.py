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
        texts.start_welcome(settings.store_url or None),
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
            texts.after_consent(settings.store_url or None),
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
    await message.answer(texts.MSG_HELP, parse_mode="HTML")
