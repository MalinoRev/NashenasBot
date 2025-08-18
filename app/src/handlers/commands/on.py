from aiogram.types import Message
from sqlalchemy import select, update

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.chat_queue import ChatQueue
from src.context.messages.callbacks.random_match import (
	get_searching_message_on,
	get_searching_message_male_on,
	get_searching_message_female_on,
	get_searching_message_nearby_on,
	get_searching_message_state_on,
)


async def handle_on_command(message: Message) -> None:
	user_id_tg = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id_tg))
		if not user or user.step != "searching":
			return
		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
		# Load latest queue row for this user
		queue: ChatQueue | None = await session.scalar(
			select(ChatQueue).where(ChatQueue.user_id == user.id).order_by(ChatQueue.id.desc())
		)
		if not queue:
			return
		# Compute bounded age range
		age = int(profile.age if profile and profile.age is not None else 0)
		frm = max(1, age - 3)
		until = min(99, age + 3)
		queue.filter_age_range_from = frm
		queue.filter_age_range_until = until
		await session.flush()
		# Delete previous searching message
		try:
			await message.bot.delete_message(chat_id=message.chat.id, message_id=queue.message_id)
		except Exception:
			pass
		# Decide which text variant to send (based on queue filters)
		text = get_searching_message_on()
		if queue.filter_only_boy:
			text = get_searching_message_male_on()
		elif queue.filter_only_girl:
			text = get_searching_message_female_on()
		elif queue.filter_only_city:
			text = get_searching_message_nearby_on()
		elif queue.filter_only_state:
			text = get_searching_message_state_on()
		# Send new searching message
		sent = await message.answer(text)
		# Update stored message id
		queue.message_id = sent.message_id
		await session.commit()


