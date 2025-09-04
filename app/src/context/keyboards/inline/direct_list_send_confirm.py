from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(kind: str, page: int) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="✅ تایید ارسال", callback_data=f"direct_list_send_confirm:{kind}:{page}"),
				InlineKeyboardButton(text="❌ عدم تایید", callback_data=f"direct_list_send_cancel:{kind}:{page}"),
			],
			[
				InlineKeyboardButton(text="✏️ ویرایش پیام", callback_data=f"direct_list_send_edit:{kind}:{page}"),
			],
		]
	)


