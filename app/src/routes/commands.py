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


@router.message(Command("help_terms"))
async def help_terms_command(message: Message) -> None:
	from src.handlers.commands.help_terms import handle_help_terms

	result = await handle_help_terms()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_onw"))
async def help_onw_command(message: Message) -> None:
	from src.handlers.commands.help_onw import handle_help_onw

	result = await handle_help_onw()
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption)
		return


@router.message(Command("help_chw"))
async def help_chw_command(message: Message) -> None:
	from src.handlers.commands.help_chw import handle_help_chw

	result = await handle_help_chw()
	await message.answer(result.get("text", ""))
	return


@router.message(Command("help_contacts"))
async def help_contacts_command(message: Message) -> None:
	from src.handlers.commands.help_contacts import handle_help_contacts

	result = await handle_help_contacts()
	await message.answer(result.get("text", ""))
	return


@router.message(Command("help_deleteMessage"))
async def help_delete_message_command(message: Message) -> None:
	from src.handlers.commands.help_deleteMessage import handle_help_delete_message

	result = await handle_help_delete_message()
	await message.answer(result.get("text", ""))
	return


@router.message(Command("help_search"))
async def help_search_command(message: Message) -> None:
	from src.handlers.commands.help_search import handle_help_search

	result = await handle_help_search()
	await message.answer(result.get("text", ""))
	return


@router.message(Command("help_shortcuts"))
async def help_shortcuts_command(message: Message) -> None:
	from src.handlers.commands.help_shortcuts import handle_help_shortcuts

	result = await handle_help_shortcuts()
	await message.answer(result.get("text", ""))
	return


# /on command while searching: enable age filter ±3 years
@router.message(Command("on"))
async def on_command(message: Message) -> None:
	from src.handlers.commands.on import handle_on_command

	await handle_on_command(message)
	return


@router.message(Command("off"))
async def off_command(message: Message) -> None:
	from src.handlers.commands.off import handle_off_command

	await handle_off_command(message)
	return


# /profile equivalent of main:profile
@router.message(Command("profile"))
async def profile_command(message: Message) -> None:
	from src.handlers.replies.profile import handle_profile
	from src.core.database import get_session
	from src.databases.users import User
	from sqlalchemy import select
	from src.context.messages.commands.id import get_message as get_id_message

	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "start":
			return

	result = await handle_profile(user_id)
	photo_path = result.get("photo_path")
	caption = result.get("caption")
	kb_inline = result.get("reply_markup")
	if photo_path and caption:
		photo = FSInputFile(photo_path)
		await message.answer_photo(photo, caption=caption, reply_markup=kb_inline)
	return


@router.message(Command("link"))
async def link_command(message: Message) -> None:
	from src.handlers.replies.my_anon_link import handle_my_anon_link
	from src.core.database import get_session
	from src.databases.users import User
	from sqlalchemy import select

	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return

	result = await handle_my_anon_link(user_id)
	await message.answer(result.get("text", ""))
	if result.get("text2"):
		await message.answer(result.get("text2"))
	return


@router.message(Command("credit"))
async def credit_command(message: Message) -> None:
	from src.handlers.replies.coin import handle_coin
	from src.core.database import get_session
	from src.databases.users import User
	from sqlalchemy import select

	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return

	result = await handle_coin(user_id)
	await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"))
	return


# /id -> send personal /user_UNIQUEID command
@router.message(Command("id"))
async def id_command(message: Message) -> None:
	from src.core.database import get_session
	from src.databases.users import User
	from sqlalchemy import select
	from src.context.messages.commands.id import get_message as get_id_message

	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return
		# Optionally gate to start like other main commands
		if user.step != "start":
			return
	await message.answer(get_id_message(user.unique_id))
	return


# /deleted_account -> show delete account flow (same as advanced:delete_account)
@router.message(Command("deleted_account"))
async def deleted_account_command(message: Message) -> None:
	from src.context.messages.callbacks.advanced_delete_account import get_message
	from src.context.keyboards.inline.advanced_delete_account import build_keyboard

	await message.answer(get_message(), reply_markup=build_keyboard())
	return


# /Instagram -> send intro + user's anon link (same as main:link second message)
@router.message(Command("Instagram"))
async def instagram_command(message: Message) -> None:
	from src.core.database import get_session
	from src.databases.users import User
	from sqlalchemy import select
	from src.context.messages.commands.instagram import get_intro
	from src.handlers.replies.my_anon_link import handle_my_anon_link
	from src.context.messages.commands.instagram_link import format_link, get_link

	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return

	await message.answer(get_intro())
	# Build fresh link from unique_id to ensure only the URL is sent
	async with get_session() as session2:
		user2: User | None = await session2.scalar(select(User).where(User.user_id == user_id))
		unique_id = user2.unique_id if user2 else None
		link = get_link(unique_id)
		if link:
			await message.answer(format_link(link))
	return

# Optional: catch-all for any other command (text starting with "/")
@router.message(F.text.startswith("/"))
async def unknown_command(message: Message) -> None:
	if message.text and message.text.startswith("/start"):
		return
	await message.answer(
		"❌ دستور مورد نظر یافت نشد\nجهت مشاهده راهنما استفاده ربات، دستور /help را بفرستید."
	)


