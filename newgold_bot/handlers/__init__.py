from aiogram import Router

from newgold_bot.handlers import dialog, start


def setup_routers() -> Router:
    root = Router()
    root.include_router(start.router)
    root.include_router(dialog.router)
    return root
