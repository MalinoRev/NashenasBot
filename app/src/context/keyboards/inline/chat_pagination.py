from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(page: int, has_next: bool, page_size: int = 10, is_active: bool = True) -> InlineKeyboardMarkup:
	# Encode direction with current page so handler can detect boundaries without double-fetch
	status_param = "active" if is_active else "completed"
	
	buttons = [
		[
			InlineKeyboardButton(text="صفحه بعدی ⬅️", callback_data=f"chat_page:next:{page}:{status_param}"),
			InlineKeyboardButton(text="➡️ صفحه قبلی", callback_data=f"chat_page:prev:{page}:{status_param}"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
