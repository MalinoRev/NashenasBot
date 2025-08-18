from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_filters import UserFilter
from src.context.messages.callbacks.advanced_chat_filter_distance import (
	get_message as get_distance_message,
)
from src.context.keyboards.inline.advanced_chat_filter_distance import (
	build_keyboard as build_distance_keyboard,
)


async def handle_advanced_chat_filter_gender_set(callback: CallbackQuery) -> None:
	data = callback.data or ""
	choice = data.split(":", 1)[1] if ":" in data else ""

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		# Load or create filter row
		uf: UserFilter | None = await session.scalar(select(UserFilter).where(UserFilter.user_id == user.id))
		if uf is None:
			uf = UserFilter(user_id=user.id)
			session.add(uf)

		if choice == "male":
			uf.only_males = True
			uf.only_females = None
		elif choice == "female":
			uf.only_females = True
			uf.only_males = None
		else:  # all
			uf.only_males = None
			uf.only_females = None

		await session.commit()

	# Go to step 2: distance prompt
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_distance_message(), reply_markup=build_distance_keyboard())
	await callback.answer()


