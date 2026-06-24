"""
My Account Handler
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import Database
from keyboards.keyboards import back_to_menu_kb

router = Router()


@router.callback_query(F.data == "my_account")
async def cb_my_account(call: CallbackQuery, db: Database):
    user = await db.get_user(call.from_user.id)
    if not user:
        await call.answer("User data not found.", show_alert=True)
        return

    total = (user["posts_random"] or 0) + (user["posts_custom"] or 0)
    join_date = (user["join_date"] or "")[:10]
    last_active = (user["last_active"] or "")[:16].replace("T", " ")
    username = f"@{user['username']}" if user.get("username") else "N/A"

    await call.message.edit_text(
        f"👤 <b>My Account</b>\n\n"
        f"👤 <b>Name:</b> {user.get('full_name', 'N/A')}\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user['telegram_id']}</code>\n"
        f"📅 <b>Joined:</b> {join_date}\n"
        f"🕐 <b>Last Active:</b> {last_active}\n\n"
        f"📊 <b>Post Statistics</b>\n"
        f"🎲 Random Mode: <b>{user['posts_random'] or 0}</b> posts\n"
        f"🛠 Custom Mode: <b>{user['posts_custom'] or 0}</b> posts\n"
        f"📝 Total Posts: <b>{total}</b>",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()
