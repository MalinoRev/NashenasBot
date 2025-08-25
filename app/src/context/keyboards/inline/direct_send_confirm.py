from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(target_unique_id: str) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="✅ تایید ارسال", callback_data=f"direct_send_confirm:{target_unique_id}"),
				InlineKeyboardButton(text="❌ عدم تایید", callback_data=f"direct_send_cancel:{target_unique_id}"),
			],
			[
				InlineKeyboardButton(text="✏️ ویرایش پیام", callback_data=f"direct_send_edit:{target_unique_id}"),
			],
		]
	)




