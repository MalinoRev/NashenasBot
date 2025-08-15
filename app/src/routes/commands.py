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
	)
	await message.answer(result.get("text", ""))


# Optional: catch-all for any other command (text starting with "/")
@router.message(F.text.startswith("/"))
async def unknown_command(message: Message) -> None:
	if message.text and message.text.startswith("/start"):
		return
	await message.answer("Unknown command.")


