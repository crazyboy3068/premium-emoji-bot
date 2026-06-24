"""
Database Access Layer (SQLite via aiosqlite)
"""

import aiosqlite
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def init(self):
        """Initialize connection and create tables."""
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._create_tables()
        await self._seed_default_packs()
        logger.info(f"Database initialized: {self.db_path}")

    async def close(self):
        if self._conn:
            await self._conn.close()

    # ═══════════════════════════════════════════════════════════
    #  TABLE CREATION
    # ═══════════════════════════════════════════════════════════

    async def _create_tables(self):
        await self._conn.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA foreign_keys=ON;

            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY,
                telegram_id     INTEGER UNIQUE NOT NULL,
                full_name       TEXT,
                username        TEXT,
                join_date       TEXT NOT NULL,
                last_active     TEXT NOT NULL,
                posts_random    INTEGER DEFAULT 0,
                posts_custom    INTEGER DEFAULT 0,
                is_blocked      INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS emoji_categories (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                emoji_icon      TEXT DEFAULT '📦',
                description     TEXT,
                telegram_link   TEXT,
                display_order   INTEGER DEFAULT 0,
                is_active       INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS emoji_packs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id     INTEGER NOT NULL,
                name            TEXT NOT NULL,
                description     TEXT,
                created_at      TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES emoji_categories(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS emoji_ids (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                pack_id         INTEGER NOT NULL,
                emoji_char      TEXT NOT NULL,
                premium_id      TEXT NOT NULL,
                label           TEXT,
                FOREIGN KEY (pack_id) REFERENCES emoji_packs(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS generated_posts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                mode            TEXT NOT NULL,
                content_type    TEXT,
                emoji_ids_used  TEXT,
                created_at      TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            );

            CREATE TABLE IF NOT EXISTS broadcasts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                message_text    TEXT,
                target          TEXT,
                sent_count      INTEGER DEFAULT 0,
                created_at      TEXT NOT NULL,
                status          TEXT DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS settings (
                key             TEXT PRIMARY KEY,
                value           TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS developer_settings (
                key             TEXT PRIMARY KEY,
                value           TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                level           TEXT,
                event           TEXT,
                user_id         INTEGER,
                detail          TEXT,
                created_at      TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
            CREATE INDEX IF NOT EXISTS idx_posts_user_id ON generated_posts(user_id);
            CREATE INDEX IF NOT EXISTS idx_posts_mode ON generated_posts(mode);
            CREATE INDEX IF NOT EXISTS idx_emoji_ids_pack ON emoji_ids(pack_id);
        """)
        await self._conn.commit()

    async def _seed_default_packs(self):
        """Insert default categories if empty."""
        async with self._conn.execute("SELECT COUNT(*) as c FROM emoji_categories") as cur:
            row = await cur.fetchone()
            if row["c"] > 0:
                return

        categories = [
            ("🎬 Movie Pack",    "🎬", "Film-themed premium emojis",            "", 1),
            ("🎮 Gaming Pack",   "🎮", "Gaming & e-sports emojis",              "", 2),
            ("🎌 Anime Pack",    "🎌", "Anime and manga inspired emojis",       "", 3),
            ("🎵 Music Pack",    "🎵", "Music and artist-related emojis",       "", 4),
            ("❤️ Love Pack",    "❤️", "Romantic and heart-themed emojis",      "", 5),
            ("📱 Social Pack",   "📱", "Social media & interaction emojis",     "", 6),
            ("🔥 Trending Pack", "🔥", "Currently trending premium emojis",     "", 7),
            ("🚀 Popular Pack",  "🚀", "Most used premium emojis",              "", 8),
            ("🕌 Islamic Pack",  "🕌", "Culturally relevant Islamic emojis",    "", 9),
        ]
        await self._conn.executemany(
            "INSERT INTO emoji_categories (name, emoji_icon, description, telegram_link, display_order) VALUES (?,?,?,?,?)",
            categories
        )

        # Default system settings
        defaults = [
            ("maintenance_mode", "0"),
            ("rate_limit", "10"),
        ]
        await self._conn.executemany(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults
        )

        # Default developer settings
        dev_defaults = [
            ("dev_name",     "Developer"),
            ("dev_username", "@developer"),
            ("dev_support",  "https://t.me/support"),
            ("dev_channel",  "https://t.me/channel"),
            ("dev_website",  ""),
            ("bot_version",  "1.0.0"),
            ("secret_key_hash", ""),  # set via admin panel
        ]
        await self._conn.executemany(
            "INSERT OR IGNORE INTO developer_settings (key, value) VALUES (?,?)", dev_defaults
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════
    #  USER OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def upsert_user(self, telegram_id: int, full_name: str, username: str):
        now = datetime.now().isoformat()
        await self._conn.execute("""
            INSERT INTO users (telegram_id, full_name, username, join_date, last_active)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                full_name   = excluded.full_name,
                username    = excluded.username,
                last_active = excluded.last_active
        """, (telegram_id, full_name, username or "", now, now))
        await self._conn.commit()

    async def get_user(self, telegram_id: int) -> Optional[Dict]:
        async with self._conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def get_all_users(self) -> List[Dict]:
        async with self._conn.execute(
            "SELECT * FROM users ORDER BY join_date DESC"
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def block_user(self, telegram_id: int, block: bool):
        await self._conn.execute(
            "UPDATE users SET is_blocked = ? WHERE telegram_id = ?",
            (1 if block else 0, telegram_id)
        )
        await self._conn.commit()

    async def is_blocked(self, telegram_id: int) -> bool:
        async with self._conn.execute(
            "SELECT is_blocked FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            row = await cur.fetchone()
            return bool(row["is_blocked"]) if row else False

    # ═══════════════════════════════════════════════════════════
    #  POST OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def log_post(self, user_id: int, mode: str, content_type: str, emoji_ids: str):
        now = datetime.now().isoformat()
        await self._conn.execute("""
            INSERT INTO generated_posts (user_id, mode, content_type, emoji_ids_used, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, mode, content_type, emoji_ids, now))

        col = "posts_random" if mode == "random" else "posts_custom"
        await self._conn.execute(
            f"UPDATE users SET {col} = {col} + 1, last_active = ? WHERE telegram_id = ?",
            (now, user_id)
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════
    #  EMOJI CATEGORIES
    # ═══════════════════════════════════════════════════════════

    async def get_categories(self) -> List[Dict]:
        async with self._conn.execute(
            "SELECT * FROM emoji_categories WHERE is_active=1 ORDER BY display_order"
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def get_category(self, cat_id: int) -> Optional[Dict]:
        async with self._conn.execute(
            "SELECT * FROM emoji_categories WHERE id = ?", (cat_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def add_category(self, name: str, icon: str, description: str):
        now = datetime.now().isoformat()
        async with self._conn.execute(
            "INSERT INTO emoji_categories (name, emoji_icon, description, created_at) VALUES (?,?,?,?)",
            (name, icon, description, now)
        ) as cur:
            await self._conn.commit()
            return cur.lastrowid

    async def update_category_link(self, cat_id: int, link: str):
        await self._conn.execute(
            "UPDATE emoji_categories SET telegram_link = ? WHERE id = ?", (link, cat_id)
        )
        await self._conn.commit()

    async def delete_category(self, cat_id: int):
        await self._conn.execute(
            "DELETE FROM emoji_categories WHERE id = ?", (cat_id,)
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════
    #  EMOJI IDs
    # ═══════════════════════════════════════════════════════════

    async def get_emoji_ids_by_category(self, cat_id: int) -> List[Dict]:
        async with self._conn.execute("""
            SELECT ei.* FROM emoji_ids ei
            JOIN emoji_packs ep ON ei.pack_id = ep.id
            WHERE ep.category_id = ?
        """, (cat_id,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def add_emoji_id(self, pack_id: int, emoji_char: str, premium_id: str, label: str):
        await self._conn.execute(
            "INSERT INTO emoji_ids (pack_id, emoji_char, premium_id, label) VALUES (?,?,?,?)",
            (pack_id, emoji_char, premium_id, label)
        )
        await self._conn.commit()

    async def get_random_premium_id(self, emoji_char: str) -> Optional[str]:
        """Get a random premium ID for a given emoji character."""
        async with self._conn.execute(
            "SELECT premium_id FROM emoji_ids WHERE emoji_char = ? ORDER BY RANDOM() LIMIT 1",
            (emoji_char,)
        ) as cur:
            row = await cur.fetchone()
            return row["premium_id"] if row else None

    # ═══════════════════════════════════════════════════════════
    #  STATISTICS
    # ═══════════════════════════════════════════════════════════

    async def get_stats(self) -> Dict:
        async with self._conn.execute("SELECT COUNT(*) as c FROM users") as cur:
            total_users = (await cur.fetchone())["c"]
        async with self._conn.execute(
            "SELECT SUM(posts_random) as r, SUM(posts_custom) as c FROM users"
        ) as cur:
            row = await cur.fetchone()
            random_posts = row["r"] or 0
            custom_posts = row["c"] or 0
        return {
            "total_users":   total_users,
            "random_posts":  random_posts,
            "custom_posts":  custom_posts,
            "total_posts":   random_posts + custom_posts,
        }

    # ═══════════════════════════════════════════════════════════
    #  SETTINGS
    # ═══════════════════════════════════════════════════════════

    async def get_setting(self, key: str) -> Optional[str]:
        async with self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ) as cur:
            row = await cur.fetchone()
            return row["value"] if row else None

    async def set_setting(self, key: str, value: str):
        await self._conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value)
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════
    #  DEVELOPER SETTINGS
    # ═══════════════════════════════════════════════════════════

    async def get_dev_setting(self, key: str) -> Optional[str]:
        async with self._conn.execute(
            "SELECT value FROM developer_settings WHERE key = ?", (key,)
        ) as cur:
            row = await cur.fetchone()
            return row["value"] if row else None

    async def set_dev_setting(self, key: str, value: str):
        await self._conn.execute(
            "INSERT OR REPLACE INTO developer_settings (key, value) VALUES (?,?)", (key, value)
        )
        await self._conn.commit()

    async def verify_secret_key(self, plain_key: str, pepper: str) -> bool:
        stored_hash = await self.get_dev_setting("secret_key_hash")
        if not stored_hash:
            return False
        test_hash = hashlib.sha256((plain_key + pepper).encode()).hexdigest()
        return test_hash == stored_hash

    async def set_secret_key(self, plain_key: str, pepper: str):
        hashed = hashlib.sha256((plain_key + pepper).encode()).hexdigest()
        await self.set_dev_setting("secret_key_hash", hashed)

    # ═══════════════════════════════════════════════════════════
    #  LOGGING
    # ═══════════════════════════════════════════════════════════

    async def write_log(self, level: str, event: str, user_id: int = None, detail: str = ""):
        now = datetime.now().isoformat()
        await self._conn.execute(
            "INSERT INTO logs (level, event, user_id, detail, created_at) VALUES (?,?,?,?,?)",
            (level, event, user_id, detail, now)
        )
        await self._conn.commit()

    # ═══════════════════════════════════════════════════════════
    #  BROADCAST
    # ═══════════════════════════════════════════════════════════

    async def log_broadcast(self, message_text: str, target: str, sent_count: int):
        now = datetime.now().isoformat()
        await self._conn.execute(
            "INSERT INTO broadcasts (message_text, target, sent_count, created_at, status) VALUES (?,?,?,?,'sent')",
            (message_text, target, sent_count, now)
        )
        await self._conn.commit()
