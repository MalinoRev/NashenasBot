from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.context.keyboards.reply.mainButtons import resolve_id_from_text as resolve_main_id


router = Router(name="replies")


@router.message()
async def handle_text_reply(message: Message) -> None:
	# This router handles plain text messages that are not commands
	if message.text and message.text.startswith("/"):
		# Let commands router handle it
		return

	text = message.text or ""
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

	await message.answer("Text received, delegating to replies or default.")


