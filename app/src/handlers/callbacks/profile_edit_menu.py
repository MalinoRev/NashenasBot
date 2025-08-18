from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.profile_edit_menu import get_message
from src.context.keyboards.inline.profile_edit_menu import build_keyboard


async def handle_profile_edit_menu(callback: CallbackQuery) -> None:
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_message(), reply_markup=build_keyboard())
	await callback.answer()


