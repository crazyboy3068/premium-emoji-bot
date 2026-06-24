"""
Start & Main Menu Handler
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from keyboards.keyboards import main_menu_kb

router = Router()

WELCOME_TEXT = (
    "👋 <b>Welcome to Premium Emoji Post Generator!</b>\n\n"
    "Transform your Telegram posts with stunning ✨ <b>premium emojis</b>.\n\n"
    "Choose an option below to get started:"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_kb())
    await call.answer()
