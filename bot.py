"""
Premium Emoji Post Generator Bot
Main entry point
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database.db import Database
from middlewares.rate_limit import RateLimitMiddleware
from middlewares.user_tracker import UserTrackerMiddleware
from handlers import (
    start,
    create_post,
    emoji_packs,
    my_account,
    help_center,
    developer,
    admin,
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    # Load config
    config = Config()

    # Init DB
    db = Database(config.DATABASE_URL)
    await db.init()

    # Init bot
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Init dispatcher with FSM storage
    dp = Dispatcher(storage=MemoryStorage())

    # Register middlewares
    dp.message.middleware(RateLimitMiddleware(rate_limit=config.RATE_LIMIT))
    dp.message.middleware(UserTrackerMiddleware(db=db))
    dp.callback_query.middleware(UserTrackerMiddleware(db=db))

    # Register routers
    dp.include_router(start.router)
    dp.include_router(create_post.router)
    dp.include_router(emoji_packs.router)
    dp.include_router(my_account.router)
    dp.include_router(help_center.router)
    dp.include_router(developer.router)
    dp.include_router(admin.router)

    # Pass shared objects
    dp["db"] = db
    dp["config"] = config

    logger.info("🤖 Bot starting...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
