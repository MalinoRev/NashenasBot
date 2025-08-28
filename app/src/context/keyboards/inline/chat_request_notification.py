from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """
    Build keyboard for chat request notification

    Args:
        request_id: The chat request ID

    Returns:
        InlineKeyboardMarkup: Keyboard with view button
    """
    print(f"LOG: build_keyboard (notification) called with request_id={request_id}")
    callback_data = f"chat_request_view:{request_id}"
    print(f"LOG: View callback_data: '{callback_data}'")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="مشاهده درخواست 👁️",
                    callback_data=callback_data
                )
            ]
        ]
    )
    print(f"LOG: Notification keyboard built successfully with {len(keyboard.inline_keyboard)} rows")
    return keyboard
