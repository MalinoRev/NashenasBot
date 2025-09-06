from aiogram.types import Message
from src.context.messages.replies.user_management_welcome import get_message as get_user_management_message
from src.context.keyboards.inline.user_management_menu import build_keyboard as build_user_management_kb


async def show_user_management(message: Message) -> None:
	"""Show user management menu"""
	await message.answer(
		get_user_management_message(),
		reply_markup=build_user_management_kb(),
		parse_mode="Markdown"
	)
