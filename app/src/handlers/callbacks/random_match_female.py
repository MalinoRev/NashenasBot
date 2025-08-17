from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.user_locations import UserLocation
from src.databases.chat_queue import ChatQueue
from src.context.messages.callbacks.random_match import (
	get_not_in_start_notice,
	get_searching_message_female,
)
from src.context.keyboards.reply.random_match import build_cancel_keyboard


async def handle_random_match_female_callback(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	# Check user step is 'start'
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "start":
			await callback.answer(get_not_in_start_notice(), show_alert=False)
			return
		# Delete the message containing the callback button
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Load profile and optional location
		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
		loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == user.id))
		# Prepare queue row (filter_only_girl=True)
		queue_row = ChatQueue(
			user_id=user.id,
			user_state_id=profile.state if profile and profile.state is not None else None,
			user_city_id=profile.city if profile and profile.city is not None else None,
			user_age=profile.age if profile and profile.age is not None else 0,
			user_location_x=(loc.location_x if loc else None),
			user_location_y=(loc.location_y if loc else None),
			filter_age_range_from=None,
			filter_age_range_until=None,
			filter_location_distance=None,
			filter_only_boy=False,
			filter_only_girl=True,
		)
		session.add(queue_row)
		# Send searching message with reply cancel button
		cancel_kb, _ = build_cancel_keyboard()
		await callback.message.answer(get_searching_message_female(), reply_markup=cancel_kb)
		# Update step to 'searching'
		user.step = "searching"
		await session.commit()



