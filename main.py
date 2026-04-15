"""Точка входа: бот NEWGOLD."""

import asyncio
import logging
import sys

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

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(setup_routers())

    logger.info("Бот NEWGOLD запущен (long polling).")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
