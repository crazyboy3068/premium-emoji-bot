"""
All inline & reply keyboards used throughout the bot.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict


# ═══════════════════════════════════════════════════════════════
#  MAIN MENU
# ═══════════════════════════════════════════════════════════════

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Create Premium Post", callback_data="create_post")],
        [InlineKeyboardButton(text="📦 Emoji Packs",        callback_data="emoji_packs")],
        [InlineKeyboardButton(text="👤 My Account",         callback_data="my_account")],
        [InlineKeyboardButton(text="📖 Help Center",        callback_data="help_center")],
        [InlineKeyboardButton(text="👨‍💻 Developer",       callback_data="developer")],
    ])


# ═══════════════════════════════════════════════════════════════
#  CREATE POST
# ═══════════════════════════════════════════════════════════════

def create_post_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Random Mode",  callback_data="mode_random")],
        [InlineKeyboardButton(text="🛠 Custom Mode",  callback_data="mode_custom")],
        [InlineKeyboardButton(text="❌ Cancel",        callback_data="main_menu")],
    ])


def post_result_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Generate Again", callback_data="generate_again")],
        [InlineKeyboardButton(text="🏠 Main Menu",      callback_data="main_menu")],
    ])


# ═══════════════════════════════════════════════════════════════
#  EMOJI PACKS
# ═══════════════════════════════════════════════════════════════

def emoji_packs_kb(categories: List[Dict]) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(
                text=cat["name"],
                callback_data=f"cat_{cat['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def category_detail_kb(cat_id: int, telegram_link: str = "") -> InlineKeyboardMarkup:
    buttons = []
    if telegram_link:
        buttons.append([
            InlineKeyboardButton(text="📢 View on Telegram", url=telegram_link)
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Back to Packs", callback_data="emoji_packs")])
    buttons.append([InlineKeyboardButton(text="🏠 Main Menu",     callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ═══════════════════════════════════════════════════════════════
#  BACK BUTTONS
# ═══════════════════════════════════════════════════════════════

def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])


def back_kb(callback: str, label: str = "🔙 Back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=callback)],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")],
    ])


# ═══════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 User Management",      callback_data="admin_users")],
        [InlineKeyboardButton(text="📢 Broadcast",            callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📦 Emoji Pack Mgmt",      callback_data="admin_packs")],
        [InlineKeyboardButton(text="📊 Statistics",           callback_data="admin_stats")],
        [InlineKeyboardButton(text="💾 Database Backup",      callback_data="admin_backup")],
        [InlineKeyboardButton(text="⚙️ System Settings",     callback_data="admin_settings")],
        [InlineKeyboardButton(text="🔐 Developer Settings",   callback_data="admin_dev_settings")],
        [InlineKeyboardButton(text="🏠 Main Menu",            callback_data="main_menu")],
    ])


def admin_users_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 View All Users",       callback_data="admin_users_list")],
        [InlineKeyboardButton(text="🔍 Search User",         callback_data="admin_users_search")],
        [InlineKeyboardButton(text="🚫 Block/Unblock User",  callback_data="admin_users_block")],
        [InlineKeyboardButton(text="🔙 Admin Panel",         callback_data="admin_panel")],
    ])


def admin_packs_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 View Categories",      callback_data="admin_cat_list")],
        [InlineKeyboardButton(text="➕ Add Category",         callback_data="admin_cat_add")],
        [InlineKeyboardButton(text="✏️ Edit Category Link",   callback_data="admin_cat_link")],
        [InlineKeyboardButton(text="🗑 Delete Category",      callback_data="admin_cat_del")],
        [InlineKeyboardButton(text="➕ Add Emoji ID",         callback_data="admin_emoji_add")],
        [InlineKeyboardButton(text="🔙 Admin Panel",         callback_data="admin_panel")],
    ])


def admin_broadcast_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Broadcast to All",      callback_data="broadcast_all")],
        [InlineKeyboardButton(text="🎯 Broadcast to Selected", callback_data="broadcast_selected")],
        [InlineKeyboardButton(text="🔙 Admin Panel",          callback_data="admin_panel")],
    ])


def admin_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Toggle Maintenance",   callback_data="settings_maintenance")],
        [InlineKeyboardButton(text="⏱ Set Rate Limit",        callback_data="settings_ratelimit")],
        [InlineKeyboardButton(text="🔙 Admin Panel",          callback_data="admin_panel")],
    ])


def confirm_kb(yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data=yes_cb),
            InlineKeyboardButton(text="❌ No",  callback_data=no_cb),
        ]
    ])
