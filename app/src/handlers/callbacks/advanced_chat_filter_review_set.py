from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.context.messages.callbacks.advanced_chat_filter_success import (
	get_message as get_success_message,
)


async def handle_advanced_chat_filter_review_set(callback: CallbackQuery) -> None:
	data = callback.data or ""
	choice = data.split(":", 1)[1] if ":" in data else ""

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
		if profile is None:
			profile = UserProfile(user_id=user.id)
			session.add(profile)

		if choice == "show":
			profile.show_filter_message = True
		else:
			profile.show_filter_message = False

		await session.commit()

	# Replace previous message and show success
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_success_message())
	await callback.answer()


