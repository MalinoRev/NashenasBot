from aiogram.types import CallbackQuery

from src.context.messages.callbacks.advanced_chat_filter_intro import (
	get_message as get_intro_message,
)
from src.context.keyboards.inline.advanced_chat_filter_gender import (
	build_keyboard as build_gender_keyboard,
)
from src.core.database import get_session
from sqlalchemy import select
from src.databases.users import User


async def handle_advanced_chat_filter(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id
	# Must be in start step
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

	try:
		await callback.message.delete()
	except Exception:
		pass

	await callback.message.answer(get_intro_message(), reply_markup=build_gender_keyboard())
	await callback.answer()


