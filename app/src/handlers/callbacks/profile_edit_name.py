from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.profileMiddleware.enterName import (
	get_message as get_enter_name_message,
)


async def handle_profile_edit_name(callback: CallbackQuery) -> None:
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		user.step = "edit_name"
		await session.commit()

	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
	await callback.answer()


