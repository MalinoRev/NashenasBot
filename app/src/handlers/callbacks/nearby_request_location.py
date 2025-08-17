from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.nearby import get_request_location_message
from src.context.keyboards.reply.nearby import build_send_location_keyboard


async def handle_nearby_request_location(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "start":
			await callback.answer("درخواست شما فقط در منوی اصلی قابل اجرا می‌باشد.")
			return
		# Delete the message containing the callback button
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Update step to sending_location
		user.step = "sending_location"
		await session.commit()
		# Show instructions with reply keyboard for sending location
		kb, _ = build_send_location_keyboard()
		await callback.message.answer(get_request_location_message(), reply_markup=kb)



