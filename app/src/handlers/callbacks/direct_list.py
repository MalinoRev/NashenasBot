from aiogram.types import CallbackQuery
from sqlalchemy import select
from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.direct_prompt import get_message as get_direct_prompt
from src.context.keyboards.reply.special_contact import build_back_keyboard as build_back_kb


async def handle_direct_list(callback: CallbackQuery) -> None:
	"""
	Handle direct list callback - set user step to collect message for list sending
	"""
	data = callback.data or ""
	if not data.startswith("direct_list:"):
		await callback.answer()
		return

	# Parse callback data: direct_list:kind:[params]:page
	parts = data.split(":")
	if len(parts) < 3:
		await callback.answer()
		return

	kind = parts[1]
	page = int(parts[-1])  # Last part is always page

	# Check if user is in start step
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or getattr(user, "step", "start") != "start":
			await callback.answer("❌ در حال حاضر نمی‌توانید از این قابلیت استفاده کنید.", show_alert=True)
			return

		# Set step for list direct message
		user.step = f"direct_list_{kind}_{page}"
		await session.commit()

	# Delete the message and show prompt
	try:
		await callback.message.delete()
	except Exception:
		pass

	kb_back, _ = build_back_kb()
	await callback.message.answer(get_direct_prompt(), reply_markup=kb_back)
	await callback.answer()

