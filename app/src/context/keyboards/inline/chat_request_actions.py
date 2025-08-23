from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(sender_unique_id: str) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="قبول درخواست ✅", callback_data=f"chat_request_accept:{sender_unique_id}"),
				InlineKeyboardButton(text="رد کردن ❌", callback_data=f"chat_request_reject:{sender_unique_id}"),
			]
		]
	)


