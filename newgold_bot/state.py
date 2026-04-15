from newgold_bot.config import Settings

_settings: Settings | None = None


def set_app_settings(s: Settings) -> None:
    global _settings
    _settings = s


def get_app_settings() -> Settings:
    if _settings is None:
        raise RuntimeError("Настройки не инициализированы.")
    return _settings
