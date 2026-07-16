from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.api import CoreSwitchClient
from bot.config import load_settings
from bot.handlers import commands_router, menu_router
from bot.middlewares import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("core-switch-bot")


async def main() -> None:
    settings = load_settings()
    api = CoreSwitchClient(settings.core_switch_base_url)

    bot = Bot(
        token=settings.telegram_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp["core_api"] = api

    auth = AuthMiddleware(settings.allowed_user_ids)
    dp.message.middleware(auth)
    dp.callback_query.middleware(auth)
    dp.include_router(commands_router)
    dp.include_router(menu_router)

    logger.info("API Core Swicht: %s", settings.core_switch_base_url)
    if settings.allowed_user_ids:
        logger.info("Usuarios permitidos: %s", sorted(settings.allowed_user_ids))
    else:
        logger.warning(
            "ALLOWED_USER_IDS vacío: cualquier usuario de Telegram puede usar el bot"
        )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot iniciado. Envía /menu en Telegram.")
        await dp.start_polling(bot)
    finally:
        await api.aclose()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
