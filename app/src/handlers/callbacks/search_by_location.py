from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.search_by_location import get_request_location_message
from src.context.keyboards.reply.nearby import build_send_location_keyboard


async def handle_search_by_location_request(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "start":
			await callback.answer("درخواست شما فقط در منوی اصلی قابل اجرا می‌باشد.")
			return
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Temporary step for location request used only for search (not persisted location)
		user.step = "search_sending_location"
		await session.commit()
		kb, _ = build_send_location_keyboard()
		await callback.message.answer(get_request_location_message(), reply_markup=kb)


