from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_locations import UserLocation
from src.context.messages.callbacks.profile_view_location import (
	get_has_location_message,
	get_missing_location_message,
)
from src.context.keyboards.inline.profile_view_location import (
	build_change_keyboard,
	build_register_keyboard,
)


async def handle_profile_view_location(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or getattr(user, "step", "start") != "start":
			await callback.answer("این عملیات فقط در منوی اصلی قابل اجراست.", show_alert=False)
			return
		# Remove the triggering message for a clean UI
		try:
			await callback.message.delete()
		except Exception:
			pass
		loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == user.id))
		if loc is None:
			await callback.message.answer(get_missing_location_message(), reply_markup=build_register_keyboard())
			return
		await callback.message.answer(get_has_location_message(), reply_markup=build_change_keyboard())



