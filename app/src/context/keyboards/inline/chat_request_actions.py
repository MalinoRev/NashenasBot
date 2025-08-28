from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(sender_unique_id: str) -> InlineKeyboardMarkup:
	print(f"LOG: build_keyboard called with sender_unique_id='{sender_unique_id}'")
	accept_data = f"chat_request_accept:{sender_unique_id}"
	reject_data = f"chat_request_reject:{sender_unique_id}"
	print(f"LOG: Accept callback_data: '{accept_data}'")
	print(f"LOG: Reject callback_data: '{reject_data}'")

	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="قبول درخواست ✅", callback_data=accept_data),
				InlineKeyboardButton(text="رد کردن ❌", callback_data=reject_data),
			]
		]
	)
	print(f"LOG: Keyboard built successfully with {len(keyboard.inline_keyboard)} rows")
	return keyboard


