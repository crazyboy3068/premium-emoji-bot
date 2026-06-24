"""
Admin Panel Handler (Owner-Only)
"""

import io
import os
import shutil
import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import Database
from keyboards.keyboards import (
    admin_panel_kb, admin_users_kb, admin_packs_kb,
    admin_broadcast_kb, admin_settings_kb,
    back_to_menu_kb, confirm_kb,
)

router = Router()
logger = logging.getLogger(__name__)


# ─── Owner filter ────────────────────────────────────────────────

def is_owner(user_id: int, config) -> bool:
    return user_id == config.OWNER_ID


class AdminStates(StatesGroup):
    # Broadcast
    broadcast_message    = State()
    broadcast_target     = State()

    # Pack management
    add_category_name    = State()
    add_category_icon    = State()
    add_category_desc    = State()
    set_category_link_id = State()
    set_category_link_url = State()
    del_category_id      = State()
    add_emoji_id_cat     = State()
    add_emoji_id_char    = State()
    add_emoji_id_pid     = State()
    add_emoji_id_label   = State()

    # User management
    search_user_query    = State()
    block_user_id        = State()

    # Settings
    set_rate_limit       = State()

    # Developer settings
    dev_key_verify       = State()
    dev_edit_field       = State()
    dev_edit_value       = State()


# ═══════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message, config):
    if not is_owner(message.from_user.id, config):
        await message.answer("🚫 Access denied.")
        return
    await message.answer("🔐 <b>Admin Panel</b>\n\nWelcome, Owner!", reply_markup=admin_panel_kb())


@router.callback_query(F.data == "admin_panel")
async def cb_admin_panel(call: CallbackQuery, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await call.message.edit_text(
        "🔐 <b>Admin Panel</b>", reply_markup=admin_panel_kb()
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════════
#  STATISTICS
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery, db: Database, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return

    stats = await db.get_stats()
    await call.message.edit_text(
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"📝 Total Posts: <b>{stats['total_posts']}</b>\n"
        f"🎲 Random Posts: <b>{stats['random_posts']}</b>\n"
        f"🛠 Custom Posts: <b>{stats['custom_posts']}</b>",
        reply_markup=admin_panel_kb()
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_users")
async def cb_admin_users(call: CallbackQuery, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await call.message.edit_text("👥 <b>User Management</b>", reply_markup=admin_users_kb())
    await call.answer()


@router.callback_query(F.data == "admin_users_list")
async def cb_users_list(call: CallbackQuery, db: Database, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return

    users = await db.get_all_users()
    if not users:
        await call.answer("No users found.", show_alert=True)
        return

    text = f"👥 <b>All Users ({len(users)})</b>\n\n"
    for u in users[:30]:
        uname = f"@{u['username']}" if u.get("username") else "no username"
        blocked = " 🚫" if u.get("is_blocked") else ""
        text += f"• <code>{u['telegram_id']}</code> — {u['full_name']} ({uname}){blocked}\n"

    if len(users) > 30:
        text += f"\n<i>...showing first 30 of {len(users)} users</i>"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_users")]
        ])
    )
    await call.answer()


@router.callback_query(F.data == "admin_users_block")
async def cb_block_user_start(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.block_user_id)
    await call.message.edit_text(
        "🚫 <b>Block/Unblock User</b>\n\n"
        "Send the user's Telegram ID.\n"
        "Example: <code>123456789</code>\n\n"
        "Prefix with <code>unblock:</code> to unblock.\n"
        "Example: <code>unblock:123456789</code>",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.block_user_id)
async def handle_block_user(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    raw = message.text.strip()
    unblock = raw.startswith("unblock:")
    user_id_str = raw.replace("unblock:", "").strip()

    if not user_id_str.isdigit():
        await message.answer("⚠️ Invalid ID. Send a numeric Telegram ID.")
        return

    uid = int(user_id_str)
    await db.block_user(uid, not unblock)
    action = "Unblocked ✅" if unblock else "Blocked 🚫"
    await db.write_log("WARN", f"admin_{action.lower()}", uid, f"by owner {message.from_user.id}")
    await state.clear()
    await message.answer(f"✅ User <code>{uid}</code> {action}.", reply_markup=admin_panel_kb())


# ═══════════════════════════════════════════════════════════════
#  BROADCAST
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast_menu(call: CallbackQuery, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await call.message.edit_text("📢 <b>Broadcast</b>", reply_markup=admin_broadcast_kb())
    await call.answer()


@router.callback_query(F.data.in_({"broadcast_all", "broadcast_selected"}))
async def cb_broadcast_start(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    target = "all" if call.data == "broadcast_all" else "selected"
    await state.update_data(broadcast_target=target)
    await state.set_state(AdminStates.broadcast_message)

    if target == "selected":
        await call.message.edit_text(
            "📢 <b>Broadcast to Selected Users</b>\n\n"
            "First, send the target user IDs (comma separated):\n"
            "Example: <code>123456,789012</code>",
            reply_markup=back_to_menu_kb()
        )
    else:
        await call.message.edit_text(
            "📢 <b>Broadcast to All Users</b>\n\nSend the message to broadcast:",
            reply_markup=back_to_menu_kb()
        )
    await call.answer()


@router.message(AdminStates.broadcast_message)
async def handle_broadcast_message(message: Message, state: FSMContext, db: Database, bot: Bot, config):
    if not is_owner(message.from_user.id, config):
        return

    data = await state.get_data()
    target = data.get("broadcast_target", "all")
    broadcast_text = message.text or message.caption or ""

    if target == "all":
        users = await db.get_all_users()
        target_ids = [u["telegram_id"] for u in users if not u.get("is_blocked")]
    else:
        # First message is IDs, second is the actual message
        if "broadcast_ids" not in data:
            ids_raw = broadcast_text
            ids = [int(i.strip()) for i in ids_raw.split(",") if i.strip().isdigit()]
            await state.update_data(broadcast_ids=ids)
            await message.answer("✅ IDs saved. Now send the message to broadcast:")
            return
        target_ids = data["broadcast_ids"]

    sent = 0
    failed = 0
    for uid in target_ids:
        try:
            if message.photo:
                await bot.send_photo(uid, message.photo[-1].file_id, caption=broadcast_text)
            elif message.video:
                await bot.send_video(uid, message.video.file_id, caption=broadcast_text)
            elif message.document:
                await bot.send_document(uid, message.document.file_id, caption=broadcast_text)
            else:
                await bot.send_message(uid, broadcast_text)
            sent += 1
        except Exception:
            failed += 1

    await db.log_broadcast(broadcast_text, target, sent)
    await state.clear()
    await message.answer(
        f"📢 <b>Broadcast Complete!</b>\n\n"
        f"✅ Sent: {sent}\n❌ Failed: {failed}",
        reply_markup=admin_panel_kb()
    )


# ═══════════════════════════════════════════════════════════════
#  EMOJI PACK MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_packs")
async def cb_admin_packs(call: CallbackQuery, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await call.message.edit_text("📦 <b>Emoji Pack Management</b>", reply_markup=admin_packs_kb())
    await call.answer()


@router.callback_query(F.data == "admin_cat_list")
async def cb_cat_list(call: CallbackQuery, db: Database, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    cats = await db.get_categories()
    text = "📂 <b>Categories</b>\n\n"
    for c in cats:
        text += f"• ID <code>{c['id']}</code> — {c['name']}\n"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Pack Mgmt", callback_data="admin_packs")]
        ])
    )
    await call.answer()


@router.callback_query(F.data == "admin_cat_add")
async def cb_cat_add(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.add_category_name)
    await call.message.edit_text(
        "➕ <b>Add Category</b>\n\nSend the category name:",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.add_category_name)
async def handle_cat_name(message: Message, state: FSMContext, config):
    if not is_owner(message.from_user.id, config):
        return
    await state.update_data(cat_name=message.text.strip())
    await state.set_state(AdminStates.add_category_icon)
    await message.answer("Send the category icon emoji (e.g. 🎬):")


@router.message(AdminStates.add_category_icon)
async def handle_cat_icon(message: Message, state: FSMContext, config):
    if not is_owner(message.from_user.id, config):
        return
    await state.update_data(cat_icon=message.text.strip())
    await state.set_state(AdminStates.add_category_desc)
    await message.answer("Send a short description:")


@router.message(AdminStates.add_category_desc)
async def handle_cat_desc(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    data = await state.get_data()
    cat_id = await db.add_category(data["cat_name"], data["cat_icon"], message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Category added! ID: <code>{cat_id}</code>",
        reply_markup=admin_panel_kb()
    )


@router.callback_query(F.data == "admin_cat_link")
async def cb_cat_link(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.set_category_link_id)
    await call.message.edit_text(
        "✏️ <b>Update Category Telegram Link</b>\n\nSend the category ID:",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.set_category_link_id)
async def handle_cat_link_id(message: Message, state: FSMContext, config):
    if not is_owner(message.from_user.id, config):
        return
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Send a numeric category ID.")
        return
    await state.update_data(link_cat_id=int(message.text.strip()))
    await state.set_state(AdminStates.set_category_link_url)
    await message.answer("Now send the Telegram link (https://t.me/...):")


@router.message(AdminStates.set_category_link_url)
async def handle_cat_link_url(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    data = await state.get_data()
    await db.update_category_link(data["link_cat_id"], message.text.strip())
    await state.clear()
    await message.answer("✅ Category link updated!", reply_markup=admin_panel_kb())


@router.callback_query(F.data == "admin_cat_del")
async def cb_cat_del(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.del_category_id)
    await call.message.edit_text(
        "🗑 <b>Delete Category</b>\n\nSend the category ID to delete:",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.del_category_id)
async def handle_cat_del(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Send a numeric category ID.")
        return
    await db.delete_category(int(message.text.strip()))
    await state.clear()
    await message.answer("✅ Category deleted!", reply_markup=admin_panel_kb())


@router.callback_query(F.data == "admin_emoji_add")
async def cb_emoji_add(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.add_emoji_id_cat)
    await call.message.edit_text(
        "➕ <b>Add Emoji ID</b>\n\nSend the category ID to add emoji to:",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.add_emoji_id_cat)
async def handle_emoji_add_cat(message: Message, state: FSMContext, config):
    if not is_owner(message.from_user.id, config):
        return
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Send a numeric category ID.")
        return
    await state.update_data(new_emoji_cat=int(message.text.strip()))
    await state.set_state(AdminStates.add_emoji_id_char)
    await message.answer("Send the emoji character (e.g. 😊):")


@router.message(AdminStates.add_emoji_id_char)
async def handle_emoji_add_char(message: Message, state: FSMContext, config):
    if not is_owner(message.from_user.id, config):
        return
    await state.update_data(new_emoji_char=message.text.strip())
    await state.set_state(AdminStates.add_emoji_id_pid)
    await message.answer("Send the Premium Emoji ID (numeric):")


@router.message(AdminStates.add_emoji_id_pid)
async def handle_emoji_add_pid(message: Message, state: FSMContext, config):
    if not is_owner(message.from_user.id, config):
        return
    await state.update_data(new_emoji_pid=message.text.strip())
    await state.set_state(AdminStates.add_emoji_id_label)
    await message.answer("Send a label/description (or send - to skip):")


@router.message(AdminStates.add_emoji_id_label)
async def handle_emoji_add_label(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    data = await state.get_data()
    label = message.text.strip()
    if label == "-":
        label = ""

    # Use pack_id = cat_id for simplicity (1:1 pack per category default)
    await db.add_emoji_id(
        pack_id=data["new_emoji_cat"],
        emoji_char=data["new_emoji_char"],
        premium_id=data["new_emoji_pid"],
        label=label
    )
    await state.clear()
    await message.answer("✅ Premium Emoji ID added!", reply_markup=admin_panel_kb())


# ═══════════════════════════════════════════════════════════════
#  DATABASE BACKUP
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_backup")
async def cb_backup(call: CallbackQuery, db: Database, bot: Bot, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return

    await call.answer("⏳ Creating backup...")
    backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    try:
        shutil.copy2(db.db_path, backup_path)
        with open(backup_path, "rb") as f:
            data = f.read()

        await bot.send_document(
            call.from_user.id,
            BufferedInputFile(data, filename=backup_path),
            caption=f"💾 <b>Database Backup</b>\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        os.remove(backup_path)
        await call.message.edit_text("✅ Backup sent to your DM!", reply_markup=admin_panel_kb())
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        await call.message.edit_text(f"❌ Backup failed: {e}", reply_markup=admin_panel_kb())


# ═══════════════════════════════════════════════════════════════
#  SYSTEM SETTINGS
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_settings")
async def cb_admin_settings(call: CallbackQuery, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await call.message.edit_text("⚙️ <b>System Settings</b>", reply_markup=admin_settings_kb())
    await call.answer()


@router.callback_query(F.data == "settings_maintenance")
async def cb_toggle_maintenance(call: CallbackQuery, db: Database, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    current = await db.get_setting("maintenance_mode")
    new_val = "0" if current == "1" else "1"
    await db.set_setting("maintenance_mode", new_val)
    status = "🔧 ON" if new_val == "1" else "✅ OFF"
    await call.message.edit_text(
        f"⚙️ Maintenance mode is now <b>{status}</b>",
        reply_markup=admin_settings_kb()
    )
    await call.answer()


@router.callback_query(F.data == "settings_ratelimit")
async def cb_set_ratelimit(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.set_rate_limit)
    await call.message.edit_text(
        "⏱ Send the new rate limit (requests per minute, e.g. 10):",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.set_rate_limit)
async def handle_set_ratelimit(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Send a numeric value.")
        return
    await db.set_setting("rate_limit", message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Rate limit updated to <b>{message.text.strip()}</b> requests/minute.",
        reply_markup=admin_panel_kb()
    )


# ═══════════════════════════════════════════════════════════════
#  DEVELOPER SETTINGS (Secret Key Protected)
# ═══════════════════════════════════════════════════════════════

DEV_FIELDS = {
    "dev_name":     "Developer Name",
    "dev_username": "Username (e.g. @username)",
    "dev_support":  "Support Link",
    "dev_channel":  "Updates Channel Link",
    "dev_website":  "Website URL",
    "bot_version":  "Bot Version",
}


@router.callback_query(F.data == "admin_dev_settings")
async def cb_dev_settings(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    await state.set_state(AdminStates.dev_key_verify)
    await call.message.edit_text(
        "🔐 <b>Developer Settings</b>\n\n"
        "⚠️ This section is protected by a <b>Secret Developer Key</b>.\n\n"
        "Enter the key to proceed:",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.dev_key_verify)
async def handle_dev_key(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return

    plain_key = message.text.strip()
    verified = await db.verify_secret_key(plain_key, config.SECRET_KEY_PEPPER)

    # Delete the key message for security
    try:
        await message.delete()
    except Exception:
        pass

    if not verified:
        await db.write_log("WARN", "dev_key_fail", message.from_user.id, "Wrong secret key")
        await message.answer(
            "❌ <b>Incorrect secret key.</b>\n\nThis attempt has been logged.",
            reply_markup=admin_panel_kb()
        )
        await state.clear()
        return

    await state.set_state(AdminStates.dev_edit_field)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    field_buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"dev_field_{key}")]
        for key, label in DEV_FIELDS.items()
    ]
    field_buttons.append([
        InlineKeyboardButton(text="🔑 Change Secret Key", callback_data="dev_field_secret_key")
    ])
    field_buttons.append([
        InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel")
    ])

    await message.answer(
        "✅ <b>Access granted!</b>\n\nSelect which field to edit:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=field_buttons)
    )


@router.callback_query(F.data.startswith("dev_field_"))
async def cb_dev_field(call: CallbackQuery, state: FSMContext, config):
    if not is_owner(call.from_user.id, config):
        await call.answer("Access denied.", show_alert=True)
        return
    field = call.data.replace("dev_field_", "")
    await state.update_data(dev_field=field)
    await state.set_state(AdminStates.dev_edit_value)

    label = DEV_FIELDS.get(field, field)
    await call.message.edit_text(
        f"✏️ <b>Edit: {label}</b>\n\nSend the new value:",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(AdminStates.dev_edit_value)
async def handle_dev_edit_value(message: Message, state: FSMContext, db: Database, config):
    if not is_owner(message.from_user.id, config):
        return
    data = await state.get_data()
    field = data.get("dev_field")
    value = message.text.strip()

    if field == "secret_key":
        await db.set_secret_key(value, config.SECRET_KEY_PEPPER)
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer("✅ Secret key updated securely!", reply_markup=admin_panel_kb())
    else:
        await db.set_dev_setting(field, value)
        await message.answer(
            f"✅ <b>{DEV_FIELDS.get(field, field)}</b> updated to: <code>{value}</code>",
            reply_markup=admin_panel_kb()
        )
    await state.clear()
