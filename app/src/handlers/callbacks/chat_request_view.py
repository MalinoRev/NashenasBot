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
    try:
        data = callback.data or ""
        parts = data.split(":", 1)
        if len(parts) < 2:
            await callback.answer()
            return

        try:
            request_id = int(parts[1])
        except ValueError:
            await callback.answer("شناسه درخواست نامعتبر است.")
            return

        # Get the chat request
        chat_request = await ChatRequestService.get_chat_request_with_users(request_id)
        if not chat_request:
            await callback.answer("درخواست چت یافت نشد.", show_alert=True)
            return

        # Check if the current user is the target
        current_user_id = callback.from_user.id if callback.from_user else 0
        if chat_request.target.user_id != current_user_id:
            await callback.answer("این درخواست برای شما نیست.", show_alert=True)
            return

        # Check if request is already processed
        if chat_request.accepted_at or chat_request.rejected_at:
            await callback.answer("این درخواست قبلاً پردازش شده است.", show_alert=True)
            return

        # Delete the notification message
        try:
            await callback.message.delete()
        except Exception:
            pass

        # Get sender's unique_id for the message
        sender_unique_id = chat_request.user.unique_id or str(chat_request.user.id)

        # Show the actual chat request message with accept/reject buttons
        message_text = chat_req_msg(sender_unique_id)
        keyboard = chat_req_actions_kb(sender_unique_id)

        await callback.message.answer(
            text=message_text,
            reply_markup=keyboard
        )

        await callback.answer()

    except Exception as e:
        print(f"ERROR: Failed to view chat request: {e}")
        await callback.answer("❌ خطا در نمایش درخواست چت.", show_alert=True)
