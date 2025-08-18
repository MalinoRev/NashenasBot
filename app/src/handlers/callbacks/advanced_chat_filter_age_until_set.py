from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_filters import UserFilter


async def handle_advanced_chat_filter_age_until_set(callback: CallbackQuery) -> None:
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
			uf.age_until = None
		else:
			try:
				age_until = int(choice)
				uf.age_until = age_until
			except ValueError:
				pass

		await session.commit()

	await callback.answer("حداکثر سن ذخیره شد.")


