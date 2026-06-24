"""
Help Center Handler
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.keyboards import back_to_menu_kb

router = Router()


def help_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 How Random Mode Works",  callback_data="help_random")],
        [InlineKeyboardButton(text="🛠 How Custom Mode Works",  callback_data="help_custom")],
        [InlineKeyboardButton(text="📦 About Emoji Packs",      callback_data="help_packs")],
        [InlineKeyboardButton(text="❓ FAQ",                    callback_data="help_faq")],
        [InlineKeyboardButton(text="🏠 Main Menu",              callback_data="main_menu")],
    ])


@router.callback_query(F.data == "help_center")
async def cb_help_center(call: CallbackQuery):
    await call.message.edit_text(
        "📖 <b>Help Center</b>\n\n"
        "Welcome! Here you'll find everything you need to know about using the bot.\n\n"
        "Select a topic below:",
        reply_markup=help_menu_kb()
    )
    await call.answer()


@router.callback_query(F.data == "help_random")
async def cb_help_random(call: CallbackQuery):
    await call.message.edit_text(
        "🎲 <b>Random Mode — How it Works</b>\n\n"
        "<b>Step 1:</b> Tap <b>✨ Create Premium Post</b> → <b>🎲 Random Mode</b>\n\n"
        "<b>Step 2:</b> Send your text, photo, video, or document.\n\n"
        "<b>Step 3:</b> The bot automatically:\n"
        "  • Scans all emojis in your content\n"
        "  • Selects premium emoji IDs from our database\n"
        "  • Replaces each emoji with its premium variant\n\n"
        "<b>Step 4:</b> Your premium post is ready to copy and share!\n\n"
        "<b>Example:</b>\n"
        "Input: <code>Hello 👋 How are you? 😊</code>\n"
        "Output: Premium emoji versions of 👋 and 😊",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Help Menu", callback_data="help_center")]
        ])
    )
    await call.answer()


@router.callback_query(F.data == "help_custom")
async def cb_help_custom(call: CallbackQuery):
    await call.message.edit_text(
        "🛠 <b>Custom Mode — Step-by-Step Guide</b>\n\n"
        "<b>Step 1:</b> Tap <b>✨ Create Premium Post</b> → <b>🛠 Custom Mode</b>\n\n"
        "<b>Step 2:</b> Send your content with emojis.\n\n"
        "<b>Step 3:</b> The bot shows you a list of detected emojis.\n\n"
        "<b>Step 4:</b> Send premium emoji IDs in the same order, one per line.\n"
        "Example:\n"
        "<code>5368324170671202286\n"
        "5368324170671202287</code>\n\n"
        "<b>Step 5:</b> The bot maps your IDs to the emojis and generates your premium post!\n\n"
        "💡 <b>Tip:</b> Find IDs in the 📦 Emoji Packs section.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Help Menu", callback_data="help_center")]
        ])
    )
    await call.answer()


@router.callback_query(F.data == "help_packs")
async def cb_help_packs(call: CallbackQuery):
    await call.message.edit_text(
        "📦 <b>Emoji Packs — What Are They?</b>\n\n"
        "Emoji Packs are curated collections of <b>Premium Emoji IDs</b> organised by theme.\n\n"
        "<b>Available categories:</b>\n"
        "🎬 Movie Pack — Film-themed emojis\n"
        "🎮 Gaming Pack — Gaming & e-sports\n"
        "🎌 Anime Pack — Anime inspired\n"
        "🎵 Music Pack — Music related\n"
        "❤️ Love Pack — Romantic themes\n"
        "📱 Social Pack — Social media\n"
        "🔥 Trending Pack — What's popular now\n"
        "🚀 Popular Pack — Most-used emojis\n"
        "🕌 Islamic Pack — Islamic culture\n\n"
        "<b>How to use:</b>\n"
        "Go to 📦 Emoji Packs → Select a category → Copy the ID you want → Use in Custom Mode!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Help Menu", callback_data="help_center")]
        ])
    )
    await call.answer()


@router.callback_query(F.data == "help_faq")
async def cb_help_faq(call: CallbackQuery):
    await call.message.edit_text(
        "❓ <b>Frequently Asked Questions</b>\n\n"
        "<b>Q: What is a Premium Emoji?</b>\n"
        "A: Premium emojis are special animated emojis available to Telegram Premium subscribers.\n\n"
        "<b>Q: Do I need Telegram Premium to use this bot?</b>\n"
        "A: To display premium emojis, the viewer needs Telegram Premium. But you can still generate posts!\n\n"
        "<b>Q: Where do I find Premium Emoji IDs?</b>\n"
        "A: Check our 📦 Emoji Packs section or use @stickers bot on Telegram.\n\n"
        "<b>Q: How many emojis can I replace at once?</b>\n"
        "A: There's no hard limit, but keep posts reasonable for best results.\n\n"
        "<b>Q: Is my content stored?</b>\n"
        "A: Only post statistics (count, mode) are stored. Content is not saved.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Help Menu", callback_data="help_center")]
        ])
    )
    await call.answer()
