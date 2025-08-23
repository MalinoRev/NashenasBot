from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.alerts.chat_target_busy import get_message as get_busy_alert
from src.context.keyboards.reply.special_contact import build_back_keyboard
from src.context.messages.callbacks.chat_request_received import format_message as chat_req_msg
from src.context.keyboards.inline.chat_request_actions import build_keyboard as chat_req_actions_kb


async def handle_visitor_profile_chat_request(callback: CallbackQuery) -> None:
	data = callback.data or ""
	# Extract unique_id from pattern profile_chat_request:{unique_id}
	parts = data.split(":", 1)
	if len(parts) < 2:
		await callback.answer()
		return
	unique_id = parts[1]
	async with get_session() as session:
		target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
		if not target:
			await callback.answer("کاربر یافت نشد.", show_alert=True)
			return
		# If target in chatting step => show alert, suggest direct
		if getattr(target, "step", "start") == "chatting":
			await callback.answer(get_busy_alert(), show_alert=True)
			return
		# Otherwise, set requester's step and notify
		viewer_id = callback.from_user.id if callback.from_user else 0
		viewer: User | None = await session.scalar(select(User).where(User.user_id == viewer_id))
		if not viewer:
			await callback.answer()
			return
		viewer.step = f"chat_request_to_{target.id}"
		await session.commit()
		try:
			await callback.message.delete()
		except Exception:
			pass
		msg = (
			f"✅ درخواست چت شما برای /user_{unique_id} ارسال شد.\n\n"
			"🚶منتظر باش تا تایید کنه..."
		)
		kb, _ = build_back_keyboard()
		await callback.message.answer(msg, reply_markup=kb)
		# Notify target with inline accept/reject
		# Resolve viewer unique_id for target message
		viewer_unique_id = viewer.unique_id or str(viewer.id)
		try:
			await callback.bot.send_message(chat_id=int(target.user_id), text=chat_req_msg(viewer_unique_id), reply_markup=chat_req_actions_kb(viewer_unique_id))
		except Exception:
			pass
		await callback.answer()
		return


