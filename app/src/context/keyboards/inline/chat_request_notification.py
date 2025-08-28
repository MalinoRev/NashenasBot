from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """
    Build keyboard for chat request notification

    Args:
        request_id: The chat request ID

    Returns:
        InlineKeyboardMarkup: Keyboard with view button
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="مشاهده درخواست 👁️",
                    callback_data=f"chat_request_view:{request_id}"
                )
            ]
        ]
    )
