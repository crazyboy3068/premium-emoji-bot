"""
Emoji Packs Handler
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import Database
from keyboards.keyboards import emoji_packs_kb, category_detail_kb, back_to_menu_kb

router = Router()


@router.callback_query(F.data == "emoji_packs")
async def cb_emoji_packs(call: CallbackQuery, db: Database):
    categories = await db.get_categories()
    if not categories:
        await call.message.edit_text(
            "📦 No emoji packs available yet.\nCheck back later!",
            reply_markup=back_to_menu_kb()
        )
        await call.answer()
        return

    await call.message.edit_text(
        "📦 <b>Emoji Packs</b>\n\n"
        "Browse our curated collections of premium emoji IDs.\n"
        "Select a category to explore:",
        reply_markup=emoji_packs_kb(categories)
    )
    await call.answer()


@router.callback_query(F.data.startswith("cat_"))
async def cb_category(call: CallbackQuery, db: Database):
    cat_id = int(call.data.split("_")[1])
    category = await db.get_category(cat_id)

    if not category:
        await call.answer("Category not found.", show_alert=True)
        return

    emoji_ids = await db.get_emoji_ids_by_category(cat_id)

    ids_text = ""
    if emoji_ids:
        ids_text = "\n\n<b>Available Premium IDs:</b>\n"
        for item in emoji_ids[:20]:  # limit display
            label = f" — {item['label']}" if item.get("label") else ""
            ids_text += f"• {item['emoji_char']} → <code>{item['premium_id']}</code>{label}\n"
        if len(emoji_ids) > 20:
            ids_text += f"\n<i>...and {len(emoji_ids)-20} more</i>"
    else:
        ids_text = "\n\n<i>No emoji IDs added to this category yet.</i>"

    desc = category.get("description") or ""
    await call.message.edit_text(
        f"{category['emoji_icon']} <b>{category['name']}</b>\n"
        f"{desc}"
        f"{ids_text}",
        reply_markup=category_detail_kb(cat_id, category.get("telegram_link") or "")
    )
    await call.answer()
