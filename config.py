"""
Configuration — loads from environment variables or .env file
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # ─── Bot ────────────────────────────────────────────────
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    # ─── Owner ──────────────────────────────────────────────
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))  # Your Telegram numeric ID

    # ─── Database ───────────────────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", "database/bot.db")

    # ─── Security ───────────────────────────────────────────
    # Developer secret key hash is stored in DB, not here
    SECRET_KEY_PEPPER: str = os.getenv("SECRET_KEY_PEPPER", "change_this_pepper_value")

    # ─── Rate Limiting ──────────────────────────────────────
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "10"))  # requests per minute

    # ─── Developer Info (defaults, editable via admin panel) ─
    DEV_NAME: str = os.getenv("DEV_NAME", "Developer")
    DEV_USERNAME: str = os.getenv("DEV_USERNAME", "@developer")
    DEV_SUPPORT: str = os.getenv("DEV_SUPPORT", "https://t.me/support")
    DEV_CHANNEL: str = os.getenv("DEV_CHANNEL", "https://t.me/channel")
    DEV_WEBSITE: str = os.getenv("DEV_WEBSITE", "")
    BOT_VERSION: str = os.getenv("BOT_VERSION", "1.0.0")
