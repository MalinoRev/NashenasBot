from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.random_match import (
	get_not_in_start_notice,
	get_searching_message,
)
from src.context.keyboards.reply.random_match import build_cancel_keyboard


async def handle_random_match_callback(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	# Check user step is 'start'
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "start":
			await callback.answer(get_not_in_start_notice(), show_alert=False)
			return
		# Delete the message containing the callback button
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Send searching message with reply cancel button
		cancel_kb, _ = build_cancel_keyboard()
		await callback.message.answer(get_searching_message(), reply_markup=cancel_kb)
		# Update step to 'searching'
		user.step = "searching"
		await session.commit()



