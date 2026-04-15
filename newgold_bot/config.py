import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    manager_chat_id: int | None
    privacy_policy_url: str
    store_url: str


def _normalize_http_url(raw: str) -> str:
    """Добавляет https://, если в .env указали домен без схемы."""
    u = raw.strip()
    if not u:
        return ""
    if not u.startswith(("http://", "https://")):
        return f"https://{u}"
    return u


def _parse_manager_chat_id(raw: str | None) -> int | None:
    if not raw or not raw.strip():
        return None
    s = raw.strip()
    try:
        return int(s)
    except ValueError:
        return None


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    mgr = _parse_manager_chat_id(os.getenv("MANAGER_CHAT_ID"))
    privacy = os.getenv("PRIVACY_POLICY_URL", "").strip()
    store = _normalize_http_url(os.getenv("STORE_URL", ""))

    return Settings(
        telegram_bot_token=token,
        manager_chat_id=mgr,
        privacy_policy_url=privacy,
        store_url=store,
    )


def validate_settings(s: Settings) -> list[str]:
    errors: list[str] = []
    if not s.telegram_bot_token:
        errors.append("TELEGRAM_BOT_TOKEN не задан.")
    if not s.privacy_policy_url:
        errors.append("PRIVACY_POLICY_URL не задан (нужна ссылка на политику).")
    return errors
