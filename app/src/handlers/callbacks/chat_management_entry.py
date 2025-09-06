from aiogram.types import Message
from src.context.messages.replies.chat_management_welcome import get_message as get_chat_management_message
from src.context.keyboards.inline.chat_management_menu import build_keyboard as build_chat_management_kb


async def show_chat_management(message: Message) -> None:
	"""Show chat management menu"""
	await message.answer(
		get_chat_management_message(),
		reply_markup=build_chat_management_kb(),
		parse_mode="Markdown"
	)
