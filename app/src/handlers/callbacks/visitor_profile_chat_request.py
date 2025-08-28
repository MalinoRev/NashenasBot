from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.chat_requests import ChatRequest
from src.services.chat_request_service import ChatRequestService
from src.context.alerts.chat_target_busy import get_message as get_busy_alert
from src.context.keyboards.reply.special_contact import build_back_keyboard
from src.context.messages.chat_request.new_chat_request_notification import get_message as get_notification_message
from src.context.keyboards.inline.chat_request_notification import build_keyboard as build_notification_keyboard


async def handle_visitor_profile_chat_request(callback: CallbackQuery) -> None:
	print("LOG: handle_visitor_profile_chat_request called")
	data = callback.data or ""
	print(f"LOG: callback.data = '{data}'")
	# Extract unique_id from pattern profile_chat_request:{unique_id}
	parts = data.split(":", 1)
	print(f"LOG: parts after split = {parts}")
	if len(parts) < 2:
		print("LOG: Not enough parts in callback data")
		await callback.answer()
		return
	unique_id = parts[1]
	print(f"LOG: extracted unique_id = '{unique_id}'")

	async with get_session() as session:
		print(f"LOG: Looking for user with unique_id '{unique_id}'")
		target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
		if not target:
			print(f"LOG: Target user with unique_id '{unique_id}' not found")
			await callback.answer("کاربر یافت نشد.", show_alert=True)
			return
		print(f"LOG: Target user found: id={target.id}, user_id={target.user_id}, unique_id='{target.unique_id}'")

		# If target in chatting step => show alert, suggest direct
		target_step = getattr(target, "step", "start")
		print(f"LOG: Target user step = '{target_step}'")
		if target_step == "chatting":
			print("LOG: Target user is currently chatting")
			await callback.answer(get_busy_alert(), show_alert=True)
			return
		# Otherwise, set requester's step and notify
		viewer_id = callback.from_user.id if callback.from_user else 0
		print(f"LOG: viewer_id = {viewer_id}")
		viewer: User | None = await session.scalar(select(User).where(User.user_id == viewer_id))
		if not viewer:
			print(f"LOG: Viewer user with user_id {viewer_id} not found")
			await callback.answer()
			return
		print(f"LOG: Viewer user found: id={viewer.id}, user_id={viewer.user_id}")

		# Check if there's an existing canceled request that needs message cleanup
		print(f"LOG: Checking for existing canceled requests from viewer.id={viewer.id} to target.id={target.id}")
		async with get_session() as temp_session:
			existing_canceled = await temp_session.scalar(
				select(ChatRequest).where(
					ChatRequest.user_id == viewer.id,
					ChatRequest.target_id == target.id,
					ChatRequest.canceled_at.isnot(None)
				)
			)
			if existing_canceled and existing_canceled.request_message_id:
				print(f"LOG: Found canceled request with message_id={existing_canceled.request_message_id}, deleting old message")
				try:
					await callback.bot.delete_message(
						chat_id=int(target.user_id),
						message_id=existing_canceled.request_message_id
					)
					print("LOG: Old message deleted successfully")
				except Exception as e:
					print(f"LOG: Failed to delete old message: {e}")

		# Save chat request to database
		print(f"LOG: Saving chat request from viewer.id={viewer.id} to target.id={target.id}")
		request_id = await ChatRequestService.save_chat_request(viewer.id, target.id)
		if not request_id:
			print("LOG: Failed to save chat request")
			await callback.answer("خطا در ارسال درخواست چت.", show_alert=True)
			return
		print(f"LOG: Chat request saved with id={request_id}")

		viewer.step = f"chat_request_to_{target.id}"
		await session.commit()
		print(f"LOG: Viewer step updated to '{viewer.step}'")

		try:
			await callback.message.delete()
			print("LOG: Profile message deleted successfully")
		except Exception as e:
			print(f"LOG: Failed to delete profile message: {e}")

		msg = (
			f"✅ درخواست چت شما برای /user_{unique_id} ارسال شد.\n\n"
			"🚶منتظر باش تا تایید کنه..."
		)
		kb, _ = build_back_keyboard()
		await callback.message.answer(msg, reply_markup=kb)
		print("LOG: Request sent message shown to viewer")

		# Send notification to target with view button
		try:
			print("LOG: Preparing notification message...")
			notification_text = get_notification_message()
			notification_keyboard = build_notification_keyboard(request_id)
			print(f"LOG: notification_text length = {len(notification_text) if notification_text else 0}")
			print(f"LOG: Sending notification to target user_id = {target.user_id}")

			sent_message = await callback.bot.send_message(
				chat_id=int(target.user_id),
				text=notification_text,
				reply_markup=notification_keyboard
			)
			print(f"LOG: Notification sent successfully, message_id = {sent_message.message_id if sent_message else 'None'}")

			# Save the message ID to the chat request
			if sent_message and sent_message.message_id:
				print(f"LOG: Updating request_message_id to {sent_message.message_id}")
				update_success = await ChatRequestService.update_request_message_id(request_id, sent_message.message_id)
				print(f"LOG: update_request_message_id result: {update_success}")
			else:
				print("LOG: No message_id to save")

		except Exception as e:
			print(f"ERROR: Failed to send chat request notification: {e}")
			import traceback
			traceback.print_exc()

		await callback.answer()
		print("LOG: handle_visitor_profile_chat_request completed successfully")
		return


