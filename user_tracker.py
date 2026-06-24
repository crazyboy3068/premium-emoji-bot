"""
User Tracker Middleware — auto-registers users on first interaction.
"""

from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from database.db import Database


class UserTrackerMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        self.db = db
        super().__init__()

    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if user:
            # Check maintenance mode
            maintenance = await self.db.get_setting("maintenance_mode")
            config = data.get("bot_data", {}).get("config")
            owner_id = None
            if config:
                owner_id = config.OWNER_ID

            if maintenance == "1" and user.id != owner_id:
                if isinstance(event, Message):
                    await event.answer("🔧 Bot is under maintenance. Please try again later.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🔧 Maintenance mode active.", show_alert=True)
                return

            # Block check
            if await self.db.is_blocked(user.id):
                if isinstance(event, Message):
                    await event.answer("🚫 You have been blocked from using this bot.")
                return

            # Register / update user
            await self.db.upsert_user(
                telegram_id=user.id,
                full_name=user.full_name,
                username=user.username
            )

        return await handler(event, data)
