"""
Create Premium Post Handler
Handles Random Mode and Custom Mode workflows via FSM.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import Database
from services.emoji_service import EmojiService
from keyboards.keyboards import create_post_kb, post_result_kb, back_to_menu_kb

router = Router()
logger = logging.getLogger(__name__)


class PostStates(StatesGroup):
    # Random Mode
    waiting_random_content = State()

    # Custom Mode
    waiting_custom_content = State()
    waiting_custom_ids      = State()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "create_post")
async def cb_create_post(call: CallbackQuery):
    await call.message.edit_text(
        "✨ <b>Create Premium Post</b>\n\n"
        "Choose your preferred mode:\n\n"
        "🎲 <b>Random Mode</b> — AI picks the best premium emojis automatically.\n"
        "🛠 <b>Custom Mode</b> — You choose which premium emoji IDs to use.",
        reply_markup=create_post_kb()
    )
    await call.answer()


# ═══════════════════════════════════════════════════════════════
#  RANDOM MODE
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "mode_random")
async def cb_mode_random(call: CallbackQuery, state: FSMContext):
    await state.set_state(PostStates.waiting_random_content)
    await call.message.edit_text(
        "🎲 <b>Random Mode</b>\n\n"
        "Send me your post content — text, photo, video, or document.\n"
        "I'll automatically replace all emojis with premium variants! ✨",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(PostStates.waiting_random_content)
async def handle_random_content(message: Message, state: FSMContext, db: Database, config):
    svc = EmojiService(db)
    text = message.text or message.caption or ""

    if not text.strip():
        await message.answer(
            "⚠️ Please send a message that contains text or a caption with emojis.",
            reply_markup=back_to_menu_kb()
        )
        return

    emoji_count = svc.count_emojis(text)

    if emoji_count == 0:
        await message.answer(
            "ℹ️ No emojis detected in your content.\n"
            "Add some emojis to your text and try again! 😊",
            reply_markup=back_to_menu_kb()
        )
        return

    # Process
    styled_text, mapping = await svc.process_random(text)

    # Log to DB
    emoji_ids_str = ", ".join(mapping.values())
    await db.log_post(
        user_id=message.from_user.id,
        mode="random",
        content_type=message.content_type.value,
        emoji_ids=emoji_ids_str
    )

    mapped_count = len(mapping)
    await state.clear()

    if message.photo:
        await message.answer_photo(
            photo=message.photo[-1].file_id,
            caption=f"✅ <b>Your Premium Post is Ready!</b>\n\n"
                    f"🔄 Replaced <b>{mapped_count}/{emoji_count}</b> emojis with premium variants.\n\n"
                    f"{styled_text}",
            reply_markup=post_result_kb()
        )
    else:
        await message.answer(
            f"✅ <b>Your Premium Post is Ready!</b>\n\n"
            f"🔄 Replaced <b>{mapped_count}/{emoji_count}</b> emojis with premium variants.\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{styled_text}\n"
            f"━━━━━━━━━━━━━━━━━━",
            reply_markup=post_result_kb()
        )


# ═══════════════════════════════════════════════════════════════
#  CUSTOM MODE
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "mode_custom")
async def cb_mode_custom(call: CallbackQuery, state: FSMContext):
    await state.set_state(PostStates.waiting_custom_content)
    await call.message.edit_text(
        "🛠 <b>Custom Mode</b>\n\n"
        "Send me your post content (text/photo/video/document).\n"
        "I'll detect all emojis and ask you for premium IDs to replace them.",
        reply_markup=back_to_menu_kb()
    )
    await call.answer()


@router.message(PostStates.waiting_custom_content)
async def handle_custom_content(message: Message, state: FSMContext):
    svc = EmojiService(None)
    text = message.text or message.caption or ""

    if not text.strip():
        await message.answer("⚠️ Please send text content.", reply_markup=back_to_menu_kb())
        return

    emojis = svc.extract_emojis(text)
    if not emojis:
        await message.answer(
            "ℹ️ No emojis found in your message. Add emojis and try again!",
            reply_markup=back_to_menu_kb()
        )
        return

    await state.update_data(
        original_text=text,
        emojis=emojis,
        content_type=message.content_type.value,
        file_id=message.photo[-1].file_id if message.photo else None,
    )
    await state.set_state(PostStates.waiting_custom_ids)

    emoji_list = "\n".join([f"  {i+1}. {e}" for i, e in enumerate(emojis)])
    await message.answer(
        f"🔍 <b>Found {len(emojis)} unique emoji(s):</b>\n\n"
        f"{emoji_list}\n\n"
        "Now send me the premium emoji IDs in the same order, "
        "one per line. Example:\n"
        "<code>5368324170671202286\n"
        "5368324170671202287</code>\n\n"
        "💡 You can get IDs from <b>📦 Emoji Packs</b> section.",
        reply_markup=back_to_menu_kb()
    )


@router.message(PostStates.waiting_custom_ids)
async def handle_custom_ids(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    original_text = data.get("original_text", "")
    emojis = data.get("emojis", [])
    content_type = data.get("content_type", "text")
    file_id = data.get("file_id")

    raw = message.text or ""
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]

    if len(lines) != len(emojis):
        await message.answer(
            f"⚠️ You sent <b>{len(lines)}</b> ID(s) but I need <b>{len(emojis)}</b>.\n"
            f"Please send exactly {len(emojis)} IDs, one per line.",
            reply_markup=back_to_menu_kb()
        )
        return

    mapping = dict(zip(emojis, lines))
    svc = EmojiService(db)
    styled_text = svc.apply_custom_mapping(original_text, mapping)

    await db.log_post(
        user_id=message.from_user.id,
        mode="custom",
        content_type=content_type,
        emoji_ids=", ".join(lines)
    )
    await state.clear()

    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=f"✅ <b>Custom Premium Post Ready!</b>\n\n{styled_text}",
            reply_markup=post_result_kb()
        )
    else:
        await message.answer(
            f"✅ <b>Custom Premium Post Ready!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{styled_text}\n"
            f"━━━━━━━━━━━━━━━━━━",
            reply_markup=post_result_kb()
        )


# ═══════════════════════════════════════════════════════════════
#  GENERATE AGAIN
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "generate_again")
async def cb_generate_again(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "✨ <b>Create Premium Post</b>\n\n"
        "Choose your mode:",
        reply_markup=create_post_kb()
    )
    await call.answer()
