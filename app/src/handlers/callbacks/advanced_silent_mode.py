from datetime import datetime

from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_settings import UserSetting
from src.context.messages.callbacks.advanced_silent_mode_status import (
	format_message as format_silent_message,
)
from src.context.keyboards.inline.advanced_silent_mode import (
	build_keyboard as build_silent_kb,
)


async def handle_advanced_silent_mode(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	silented_until: datetime | None = None
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if user:
			settings: UserSetting | None = await session.scalar(
				select(UserSetting).where(UserSetting.user_id == user.id)
			)
			silented_until = settings.silented_until if settings else None
	status_text = "غیرفعال"
	is_active = False
	if silented_until is not None:
		try:
			status_text = f"فعال تا {silented_until.strftime('%Y-%m-%d %H:%M')}"
			is_active = True
		except Exception:
			status_text = "فعال"
			is_active = True
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(
		format_silent_message(status_text), reply_markup=build_silent_kb(is_active=is_active)
	)
	await callback.answer()


