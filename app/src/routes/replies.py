from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, LinkPreviewOptions
from src.context.keyboards.reply.mainButtons import resolve_id_from_text as resolve_main_id
from src.context.keyboards.reply.random_match import resolve_id_from_text as resolve_random_match_reply_id
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb
from src.context.messages.commands.start import get_message as get_start_message


router = Router(name="replies")


@router.message()
async def handle_text_reply(message: Message) -> None:
	# This router handles plain text messages that are not commands
	if message.text and message.text.startswith("/"):
		# Let commands router handle it
		return

	text = message.text or ""

	# Handle random_match cancel reply button
	rm_id = resolve_random_match_reply_id(text)
	if rm_id == "random_match:cancel":
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.chat_queue import ChatQueue
		from sqlalchemy import select, delete

		user_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "searching":
				return
			# Delete any queue records for this user (by internal users.id)
			await session.execute(delete(ChatQueue).where(ChatQueue.user_id == user.id))
			# Set step back to start
			user.step = "start"
			await session.commit()
		# Send the same start message + main keyboard as /start
		name = (message.from_user.first_name if message.from_user else None) or (message.from_user.username if message.from_user else None)
		start_text = get_start_message(name)
		kb, _ = build_main_kb()
		await message.answer(
			start_text,
			reply_markup=kb,
			parse_mode="Markdown",
			link_preview_options=LinkPreviewOptions(is_disabled=True),
		)
		return

	main_id = resolve_main_id(text)
	if main_id == "main:my_anon_link":
		from src.handlers.replies.my_anon_link import handle_my_anon_link
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				# User step is not 'start', don't send anything
				return
		
		# User step is 'start', proceed with handler
		result = await handle_my_anon_link(user_id)
		
		# Send first message
		await message.answer(result.get("text", ""))
		
		# Send second message
		if result.get("text2"):
			await message.answer(result.get("text2"))
		return

	if main_id == "main:random_match":
		from src.handlers.replies.random_match import handle_random_match
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_random_match()
		await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"))
		return

	if main_id == "main:invite":
		from src.handlers.replies.invite import handle_invite
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_invite(user_id)
		# Send photo with caption first
		photo_path = result.get("photo_path")
		caption = result.get("caption")
		if photo_path and caption:
			photo = FSInputFile(photo_path)
			await message.answer_photo(photo, caption=caption)
		# Then send second text message if any
		if result.get("text"):
			await message.answer(result.get("text"))
		return

	if main_id == "main:help":
		from src.handlers.replies.help import handle_help
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_help()
		await message.answer(result.get("text", ""))
		return

	await message.answer("Text received, delegating to replies or default.")


