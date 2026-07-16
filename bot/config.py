import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    core_switch_base_url: str
    allowed_user_ids: frozenset[int]


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN no está configurado en .env")

    base_url = (
        os.getenv("CORE_SWITCH_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")
    )

    raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
    allowed: set[int] = set()
    if raw_ids:
        for part in raw_ids.split(","):
            part = part.strip()
            if part:
                allowed.add(int(part))

    return Settings(
        telegram_token=token,
        core_switch_base_url=base_url,
        allowed_user_ids=frozenset(allowed),
    )
