"""Точка входа: бот NEWGOLD."""

import asyncio
import logging
import sys
import traceback

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from newgold_bot.config import load_settings, validate_settings
from newgold_bot.handlers import setup_routers
from newgold_bot.state import set_app_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = load_settings()
    errors = validate_settings(settings)
    if errors:
        for e in errors:
            logger.error("%s", e)
        sys.exit(1)

    set_app_settings(settings)
    logger.info("Настройки загружены из .env (корень проекта).")

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(setup_routers())

    me = await bot.get_me()
    logger.info("Токен верный, бот: @%s (id=%s)", me.username or "—", me.id)

    # Сброс webhook и очереди — иначе long polling может не получать апдейты.
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook сброшен, ожидание сообщений (long polling)...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка по Ctrl+C.")
    except Exception:
        logger.error("Фатальная ошибка:\n%s", traceback.format_exc())
        sys.exit(1)
