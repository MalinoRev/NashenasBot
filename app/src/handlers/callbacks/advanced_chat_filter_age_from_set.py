from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_filters import UserFilter
from src.context.messages.callbacks.advanced_chat_filter_age_until import (
	get_message as get_age_until_message,
)
from src.context.keyboards.inline.advanced_chat_filter_age_until import (
	build_keyboard as build_age_until_keyboard,
)


async def handle_advanced_chat_filter_age_from_set(callback: CallbackQuery) -> None:
	data = callback.data or ""
	choice = data.split(":", 1)[1] if ":" in data else ""

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		uf: UserFilter | None = await session.scalar(select(UserFilter).where(UserFilter.user_id == user.id))
		if uf is None:
			uf = UserFilter(user_id=user.id)
			session.add(uf)

		if choice == "all":
			uf.age_from = None
			uf.age_until = None
		else:
			try:
				age_from = int(choice)
				uf.age_from = age_from
				# Do not change age_until yet; next step will set it
			except ValueError:
				pass

		await session.commit()

	# Move to "until" step
	try:
		await callback.message.delete()
	except Exception:
		pass
	min_age = uf.age_from if ("all" != choice) else None
	await callback.message.answer(
		get_age_until_message(min_age), reply_markup=build_age_until_keyboard(min_age)
	)
	await callback.answer()


