from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


router = Router(name="commands")


@router.message(CommandStart())
async def start_command(message: Message) -> None:
	from src.handlers.commands.start import handle_start

	user = message.from_user
	chat = message.chat
	result = await handle_start(
		user_id=user.id if user else 0,
		chat_id=chat.id,
		username=user.username if user else None,
		message_id=message.message_id,
		first_name=user.first_name if user else None,
		last_name=user.last_name if user else None,
		language_code=user.language_code if user else None,
	)
	await message.answer(result.get("text", ""))


# Optional: catch-all for any other command (text starting with "/")
@router.message(F.text.startswith("/"))
async def unknown_command(message: Message) -> None:
	if message.text and message.text.startswith("/start"):
		return
	await message.answer("Unknown command.")


