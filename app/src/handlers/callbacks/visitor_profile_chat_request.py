from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.services.chat_request_service import ChatRequestService
from src.context.alerts.chat_target_busy import get_message as get_busy_alert
from src.context.keyboards.reply.special_contact import build_back_keyboard
from src.context.messages.chat_request.new_chat_request_notification import get_message as get_notification_message
from src.context.keyboards.inline.chat_request_notification import build_keyboard as build_notification_keyboard


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
		# Save chat request to database
		request_id = await ChatRequestService.save_chat_request(viewer.id, target.id)
		if not request_id:
			await callback.answer("خطا در ارسال درخواست چت.", show_alert=True)
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

		# Send notification to target with view button
		try:
			notification_text = get_notification_message()
			notification_keyboard = build_notification_keyboard(request_id)
			await callback.bot.send_message(
				chat_id=int(target.user_id),
				text=notification_text,
				reply_markup=notification_keyboard
			)
		except Exception as e:
			print(f"ERROR: Failed to send chat request notification: {e}")

		await callback.answer()
		return


