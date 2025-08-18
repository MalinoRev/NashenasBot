from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_settings import UserSetting
from src.context.messages.callbacks.advanced_alarms import format_message
from src.context.keyboards.inline.advanced_alarms import build_keyboard


async def handle_advanced_alarms_toggle(callback: CallbackQuery) -> None:
	data = callback.data or ""
	which = data.split(":", 1)[1] if ":" in data else ""

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		settings: UserSetting | None = await session.scalar(
			select(UserSetting).where(UserSetting.user_id == user.id)
		)
		if settings is None:
			settings = UserSetting(user_id=user.id)
			session.add(settings)

		if which == "visit_toggle":
			settings.profile_visit_alarm = not bool(settings.profile_visit_alarm)
		elif which == "like_toggle":
			settings.profile_like_alarm = not bool(settings.profile_like_alarm)

		await session.commit()

	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(
		format_message(settings.profile_visit_alarm, settings.profile_like_alarm),
		reply_markup=build_keyboard(settings.profile_visit_alarm, settings.profile_like_alarm),
	)
	await callback.answer()


