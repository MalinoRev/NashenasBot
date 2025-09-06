from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(page: int, has_next: bool, page_size: int = 10, user_type: str = "banned") -> InlineKeyboardMarkup:
	# Encode direction with current page so handler can detect boundaries without double-fetch
	buttons = [
		[
			InlineKeyboardButton(text="صفحه بعدی ⬅️", callback_data=f"user_page:next:{page}:{user_type}"),
			InlineKeyboardButton(text="➡️ صفحه قبلی", callback_data=f"user_page:prev:{page}:{user_type}"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
