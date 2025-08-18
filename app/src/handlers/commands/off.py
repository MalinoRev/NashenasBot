from aiogram.types import Message
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.chat_queue import ChatQueue
from src.context.messages.callbacks.random_match import (
	get_searching_message,
	get_searching_message_male,
	get_searching_message_female,
	get_searching_message_nearby,
	get_searching_message_state,
)


async def handle_off_command(message: Message) -> None:
	user_id_tg = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id_tg))
		if not user or user.step != "searching":
			return
		# Load latest queue row for this user
		queue: ChatQueue | None = await session.scalar(
			select(ChatQueue).where(ChatQueue.user_id == user.id).order_by(ChatQueue.id.desc())
		)
		if not queue:
			return
		# Remove age filters
		queue.filter_age_range_from = None
		queue.filter_age_range_until = None
		await session.flush()
		# Delete previous searching message
		try:
			await message.bot.delete_message(chat_id=message.chat.id, message_id=queue.message_id)
		except Exception:
			pass
		# Decide which text variant to send (based on queue filters)
		text = get_searching_message()
		if queue.filter_only_boy:
			text = get_searching_message_male()
		elif queue.filter_only_girl:
			text = get_searching_message_female()
		elif queue.filter_only_city:
			text = get_searching_message_nearby()
		elif queue.filter_only_state:
			text = get_searching_message_state()
		# Send new searching message
		sent = await message.answer(text)
		# Update stored message id
		queue.message_id = sent.message_id
		await session.commit()


