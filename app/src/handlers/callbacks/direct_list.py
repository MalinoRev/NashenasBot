from aiogram.types import CallbackQuery
from sqlalchemy import select
import re
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

	# Extract recipients from current message by parsing /user_UNIQUEID entries
	text = callback.message.text or ""
	unique_ids = re.findall(r"/user_([A-Za-z0-9_]+)", text)
	if not unique_ids:
		await callback.answer("لیستی برای ارسال یافت نشد.", show_alert=True)
		return

	# Check if user is in start step
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or getattr(user, "step", "start") != "start":
			await callback.answer("❌ در حال حاضر نمی‌توانید از این قابلیت استفاده کنید.", show_alert=True)
			return

		# Map unique_ids to internal user ids
		from src.databases.users import User as _U
		recipients: list[int] = []
		for uid in unique_ids:
			u: _U | None = await session.scalar(select(_U).where(_U.unique_id == uid))
			if u and u.id != (user.id if user else 0):
				recipients.append(int(u.id))
		# Deduplicate and limit to avoid step overflow
		recipients = list(dict.fromkeys(recipients))[:20]
		ids_token = "-".join(str(i) for i in recipients)
		# Set step for list direct message with stabilized recipient ids
		user.step = f"direct_list_to_{ids_token}"
		await session.commit()

	# Delete the message and show prompt
	try:
		await callback.message.delete()
	except Exception:
		pass

	kb_back, _ = build_back_kb()
	await callback.message.answer(get_direct_prompt(), reply_markup=kb_back)
	await callback.answer()

