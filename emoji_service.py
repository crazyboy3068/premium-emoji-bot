"""
Emoji Service — detects, maps, and replaces emojis with premium variants.
"""

import re
import emoji
import logging
from typing import List, Tuple, Dict, Optional
from database.db import Database

logger = logging.getLogger(__name__)

# Regex to detect emoji characters
EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"
    "\u3030"
    "]+",
    flags=re.UNICODE,
)


class EmojiService:
    def __init__(self, db: Database):
        self.db = db

    def extract_emojis(self, text: str) -> List[str]:
        """Return list of unique emojis found in text."""
        found = EMOJI_PATTERN.findall(text)
        unique = list(dict.fromkeys(found))
        return unique

    def count_emojis(self, text: str) -> int:
        return len(EMOJI_PATTERN.findall(text))

    async def build_random_mapping(self, text: str) -> Dict[str, str]:
        """
        For each emoji in text, fetch a random premium ID from DB.
        Returns {emoji_char: premium_id}.
        """
        emojis = self.extract_emojis(text)
        mapping: Dict[str, str] = {}
        for e in emojis:
            pid = await self.db.get_random_premium_id(e)
            if pid:
                mapping[e] = pid
        return mapping

    def apply_premium_mapping(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Replace standard emojis with Telegram CustomEmoji tags.
        Format: <tg-emoji emoji-id="ID">ORIGINAL</tg-emoji>
        """
        result = text
        for emoji_char, premium_id in mapping.items():
            replacement = f'<tg-emoji emoji-id="{premium_id}">{emoji_char}</tg-emoji>'
            result = result.replace(emoji_char, replacement)
        return result

    async def process_random(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Full random-mode pipeline.
        Returns (styled_text, mapping_used).
        """
        mapping = await self.build_random_mapping(text)
        styled = self.apply_premium_mapping(text, mapping)
        return styled, mapping

    def apply_custom_mapping(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Apply user-provided mapping (emoji → premium_id).
        """
        return self.apply_premium_mapping(text, mapping)

    def format_post(self, content: str, title: str = "") -> str:
        """
        Wrap content in a styled post format.
        """
        if title:
            return f"<b>{title}</b>\n\n{content}"
        return content
