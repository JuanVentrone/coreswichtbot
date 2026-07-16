from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class AuthMiddleware(BaseMiddleware):
    """If ALLOWED_USER_IDS is set, only those users can use the bot."""

    def __init__(self, allowed_user_ids: frozenset[int]) -> None:
        self.allowed_user_ids = allowed_user_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not self.allowed_user_ids:
            return await handler(event, data)

        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user is None or user.id not in self.allowed_user_ids:
            if isinstance(event, Message):
                await event.answer("⛔ No autorizado.")
            elif isinstance(event, CallbackQuery):
                await event.answer("No autorizado", show_alert=True)
            return None

        return await handler(event, data)
