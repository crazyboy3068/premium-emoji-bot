"""
Developer Section Handler
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database

router = Router()


@router.callback_query(F.data == "developer")
async def cb_developer(call: CallbackQuery, db: Database):
    dev_name     = await db.get_dev_setting("dev_name")     or "Developer"
    dev_username = await db.get_dev_setting("dev_username") or "@developer"
    dev_support  = await db.get_dev_setting("dev_support")  or ""
    dev_channel  = await db.get_dev_setting("dev_channel")  or ""
    dev_website  = await db.get_dev_setting("dev_website")  or ""
    bot_version  = await db.get_dev_setting("bot_version")  or "1.0.0"

    buttons = []
    if dev_support:
        buttons.append([InlineKeyboardButton(text="💬 Support", url=dev_support)])
    if dev_channel:
        buttons.append([InlineKeyboardButton(text="📢 Updates Channel", url=dev_channel)])
    if dev_website:
        buttons.append([InlineKeyboardButton(text="🌐 Website", url=dev_website)])
    buttons.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])

    website_line = f"\n🌐 <b>Website:</b> {dev_website}" if dev_website else ""

    await call.message.edit_text(
        f"👨‍💻 <b>Developer Information</b>\n\n"
        f"👤 <b>Name:</b> {dev_name}\n"
        f"📱 <b>Contact:</b> {dev_username}\n"
        f"🤖 <b>Bot Version:</b> v{bot_version}"
        f"{website_line}\n\n"
        f"<i>For support, bug reports, or feature requests, reach out via the links below.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await call.answer()
