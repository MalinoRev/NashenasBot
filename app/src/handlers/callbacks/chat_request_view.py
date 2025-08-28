from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.services.chat_request_service import ChatRequestService
from src.context.messages.callbacks.chat_request_received import format_message as chat_req_msg
from src.context.keyboards.inline.chat_request_actions import build_keyboard as chat_req_actions_kb


async def handle_chat_request_view(callback: CallbackQuery) -> None:
    """
    Handle viewing a chat request - shows the actual request with accept/reject buttons
    """
    print("LOG: handle_chat_request_view called")
    try:
        data = callback.data or ""
        print(f"LOG: callback.data = '{data}'")
        parts = data.split(":", 1)
        print(f"LOG: parts after split = {parts}")
        if len(parts) < 2:
            print("LOG: Not enough parts in callback data")
            await callback.answer()
            return

        try:
            request_id = int(parts[1])
            print(f"LOG: extracted request_id = {request_id}")
        except ValueError as e:
            print(f"LOG: Failed to parse request_id: {e}")
            await callback.answer("شناسه درخواست نامعتبر است.")
            return

        # Get the chat request
        print(f"LOG: Getting chat request with id {request_id}")
        chat_request = await ChatRequestService.get_chat_request_with_users(request_id)
        if not chat_request:
            print(f"LOG: Chat request {request_id} not found")
            await callback.answer("درخواست چت یافت نشد.", show_alert=True)
            return

        print(f"LOG: Chat request found: id={chat_request.id}, user_id={chat_request.user_id}, target_id={chat_request.target_id}")

        # Check if the current user is the target
        current_user_id = callback.from_user.id if callback.from_user else 0
        print(f"LOG: current_user_id = {current_user_id}")
        print(f"LOG: chat_request.target.user_id = {chat_request.target.user_id}")

        if chat_request.target.user_id != current_user_id:
            print(f"LOG: User mismatch! Current user {current_user_id} is not target {chat_request.target.user_id}")
            await callback.answer("این درخواست برای شما نیست.", show_alert=True)
            return

        print("LOG: User is the target, checking request status...")

        # Check if request is already processed or canceled
        if chat_request.accepted_at or chat_request.rejected_at:
            print(f"LOG: Request already processed - accepted: {chat_request.accepted_at}, rejected: {chat_request.rejected_at}")
            await callback.answer("این درخواست قبلاً پردازش شده است.", show_alert=True)
            return

        if chat_request.canceled_at:
            print(f"LOG: Request was canceled at {chat_request.canceled_at}")
            await callback.answer("این درخواست چت توسط ارسال‌کننده کنسل شده است.", show_alert=True)
            return

        print("LOG: Request is valid, deleting notification message...")

        # Delete the notification message
        try:
            await callback.message.delete()
            print("LOG: Notification message deleted successfully")
        except Exception as e:
            print(f"LOG: Failed to delete notification message: {e}")

        # Get sender's unique_id for the message
        sender_unique_id = chat_request.user.unique_id or str(chat_request.user.id)
        print(f"LOG: sender_unique_id = '{sender_unique_id}'")

        # Show the actual chat request message with accept/reject buttons
        print("LOG: Formatting chat request message...")
        message_text = chat_req_msg(sender_unique_id)
        keyboard = chat_req_actions_kb(sender_unique_id)
        print(f"LOG: message_text length = {len(message_text) if message_text else 0}")
        print(f"LOG: keyboard created successfully")

        print("LOG: Sending chat request message...")
        sent_message = await callback.message.answer(
            text=message_text,
            reply_markup=keyboard
        )
        print(f"LOG: Message sent successfully, message_id = {sent_message.message_id if sent_message else 'None'}")

        # Update request_message_id with the new message ID
        if sent_message and sent_message.message_id:
            print(f"LOG: Updating request_message_id to {sent_message.message_id}")
            success = await ChatRequestService.update_request_message_id(request_id, sent_message.message_id)
            print(f"LOG: update_request_message_id result: {success}")
        else:
            print("LOG: No message_id to update")

        await callback.answer()
        print("LOG: handle_chat_request_view completed successfully")

    except Exception as e:
        print(f"ERROR: Failed to view chat request: {e}")
        import traceback
        traceback.print_exc()
        await callback.answer("❌ خطا در نمایش درخواست چت.", show_alert=True)
