from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_filters import UserFilter
from src.context.messages.callbacks.advanced_chat_filter_age_from import (
	get_message as get_age_from_message,
)
from src.context.keyboards.inline.advanced_chat_filter_age_from import (
	build_keyboard as build_age_from_keyboard,
)


async def handle_advanced_chat_filter_distance_set(callback: CallbackQuery) -> None:
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
			uf.same_state = None
			uf.same_city = None
			uf.distance_limit = None
		elif choice == "same_state":
			uf.same_state = True
			uf.same_city = None
			uf.distance_limit = None
		elif choice == "not_same_state":
			uf.same_state = False
			uf.same_city = None
			uf.distance_limit = None
		elif choice == "same_city":
			uf.same_city = True
			uf.same_state = None
			uf.distance_limit = None
		elif choice == "not_same_city":
			uf.same_city = False
			uf.same_state = None
			uf.distance_limit = None
		elif choice == "lt_100":
			uf.distance_limit = 100
			uf.same_state = None
			uf.same_city = None
		elif choice == "lt_10":
			uf.distance_limit = 10
			uf.same_state = None
			uf.same_city = None

		await session.commit()

	# Advance to age-from step
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_age_from_message(), reply_markup=build_age_from_keyboard())
	await callback.answer()


