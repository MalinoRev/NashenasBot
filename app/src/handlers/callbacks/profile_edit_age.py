from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.profileMiddleware.chooseAge import get_message as get_choose_age_message
from src.context.keyboards.reply.age import build_keyboard as build_age_kb


async def handle_profile_edit_age(callback: CallbackQuery) -> None:
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		user.step = "edit_age"
		await session.commit()

	try:
		await callback.message.delete()
	except Exception:
		pass
	age_kb, _ = build_age_kb()
	await callback.message.answer(get_choose_age_message(), reply_markup=age_kb)
	await callback.answer()


