from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, LinkPreviewOptions, FSInputFile


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


@router.message(Command("help"))
async def help_command(message: Message) -> None:
	from src.handlers.commands.help import handle_help

	result = await handle_help()
	await message.answer(result.get("text", ""))
	return


@router.message(Command("help_chat"))
async def help_chat_command(message: Message) -> None:
	from src.handlers.commands.help_chat import handle_help_chat

	result = await handle_help_chat()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_credit"))
async def help_credit_command(message: Message) -> None:
	from src.handlers.commands.help_credit import handle_help_credit

	result = await handle_help_credit()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_gps"))
async def help_gps_command(message: Message) -> None:
	from src.handlers.commands.help_gps import handle_help_gps

	result = await handle_help_gps()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_profile"))
async def help_profile_command(message: Message) -> None:
	from src.handlers.commands.help_profile import handle_help_profile

	result = await handle_help_profile()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_pchat"))
async def help_pchat_command(message: Message) -> None:
	from src.handlers.commands.help_pchat import handle_help_pchat

	result = await handle_help_pchat()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_direct"))
async def help_direct_command(message: Message) -> None:
	from src.handlers.commands.help_direct import handle_help_direct

	result = await handle_help_direct()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


# Optional: catch-all for any other command (text starting with "/")
@router.message(F.text.startswith("/"))
async def unknown_command(message: Message) -> None:
	if message.text and message.text.startswith("/start"):
		return
	await message.answer("Unknown command.")


