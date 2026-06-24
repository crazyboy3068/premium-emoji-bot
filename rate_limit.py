"""
Rate Limiting Middleware — limits requests per user per minute.
"""

import time
import logging
from collections import defaultdict, deque
from typing import Callable, Dict, Any, Deque
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = 10):
        self.rate_limit = rate_limit  # max requests per 60 seconds
        self._user_timestamps: Dict[int, Deque[float]] = defaultdict(deque)
        super().__init__()

    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None
        if not user_id:
            return await handler(event, data)

        now = time.monotonic()
        window = 60.0
        timestamps = self._user_timestamps[user_id]

        # Remove old timestamps outside the window
        while timestamps and now - timestamps[0] > window:
            timestamps.popleft()

        if len(timestamps) >= self.rate_limit:
            wait = window - (now - timestamps[0])
            await event.answer(
                f"⚠️ Too many requests. Please wait <b>{wait:.0f}s</b> before trying again.",
                parse_mode="HTML"
            )
            logger.warning(f"Rate limit hit: user {user_id}")
            return

        timestamps.append(now)
        return await handler(event, data)
