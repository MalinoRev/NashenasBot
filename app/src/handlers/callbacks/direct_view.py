from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.services.direct_service import DirectService


async def handle_direct_view(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("direct_view:"):
		await callback.answer()
		return

	direct_id_str = data.split(":", 1)[1]
	try:
		direct_id = int(direct_id_str)
	except ValueError:
		await callback.answer("❌ شناسه پیام نامعتبر", show_alert=True)
		return

	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer()
			return

		# Initialize service
		direct_service = DirectService(callback.message.bot)

		# Send direct message to user
		success = await direct_service.send_direct_to_user(direct_id, user_id)

		if success:
			try:
				await callback.message.edit_text("✅ پیام دایرکت نمایش داده شد.")
			except Exception:
				await callback.message.answer("✅ پیام دایرکت نمایش داده شد.")
		else:
			try:
				await callback.message.edit_text("❌ خطا در نمایش پیام دایرکت.")
			except Exception:
				await callback.message.answer("❌ خطا در نمایش پیام دایرکت.")

		await callback.answer()
