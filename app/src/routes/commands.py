from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, LinkPreviewOptions


router = Router(name="commands")


@router.message(CommandStart())
async def start_command(message: Message) -> None:
	# Use contextualized message and keyboard, without touching their files
	from src.context.messages.commands.start import get_message as get_start_message
	from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb

	name = None
	if message.from_user:
		name = message.from_user.first_name or message.from_user.username or None
	text = get_start_message(name)
	kb, _ = build_main_kb()
	await message.answer(
		text,
		reply_markup=kb,
		parse_mode="Markdown",
		link_preview_options=LinkPreviewOptions(is_disabled=True),
	)


# Optional: catch-all for any other command (text starting with "/")
@router.message(F.text.startswith("/"))
async def unknown_command(message: Message) -> None:
	if message.text and message.text.startswith("/start"):
		return
	await message.answer("Unknown command.")


