from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router(name="replies")


@router.message()
async def handle_text_reply(message: Message) -> None:
	# This router handles plain text messages that are not commands
	if message.text and message.text.startswith("/"):
		# Let commands router handle it
		return
	await message.answer("Text received, delegating to replies or default.")


