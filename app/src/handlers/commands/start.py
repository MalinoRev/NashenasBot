from typing import Optional
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.context.messages.commands.start import get_message as get_start_message
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb


router = Router(name="commands")


@router.message(CommandStart())
async def start_command(message: Message) -> None:
	user = message.from_user
	name: Optional[str] = None
	if user:
		name = user.first_name or user.username or None
	text = get_start_message(name)
	kb, _ = build_main_kb()
	await message.answer(text, reply_markup=kb)


