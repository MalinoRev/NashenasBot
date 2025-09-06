from aiogram.types import Message
from src.context.messages.replies.statistics_welcome import get_message as get_statistics_welcome_message
from src.context.keyboards.inline.statistics_main_menu import build_keyboard as build_statistics_main_kb


async def show_statistics(message: Message) -> None:
	"""Show statistics menu"""
	await message.answer(
		get_statistics_welcome_message(),
		reply_markup=build_statistics_main_kb(),
		parse_mode="Markdown"
	)
