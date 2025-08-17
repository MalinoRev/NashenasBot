from datetime import datetime, timedelta, timezone

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


async def handle_advanced_silent_mode_set(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	choice = (callback.data or "").split(":", 1)[-1]
	now = datetime.now(timezone.utc)
	new_until: datetime | None
	if choice == "30m":
		new_until = now + timedelta(minutes=30)
	elif choice == "1h":
		new_until = now + timedelta(hours=1)
	elif choice == "forever":
		# Far future (e.g., 50 years)
		new_until = now + timedelta(days=365 * 50)
	elif choice == "off":
		new_until = None
	else:
		new_until = None
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer("کاربر یافت نشد")
			return
		settings: UserSetting | None = await session.scalar(
			select(UserSetting).where(UserSetting.user_id == user.id)
		)
		if settings is None:
			settings = UserSetting(user_id=user.id, silented_until=new_until)
			session.add(settings)
		else:
			settings.silented_until = new_until
		await session.commit()
	status_text = (f"فعال تا {new_until.strftime('%Y-%m-%d %H:%M')}" if new_until else "غیرفعال")
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(
		format_silent_message(status_text),
		reply_markup=build_silent_kb(is_active=new_until is not None),
	)
	await callback.answer("بروزرسانی شد")


