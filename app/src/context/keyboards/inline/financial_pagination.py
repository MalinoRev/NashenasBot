from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(page: int, has_next: bool, page_size: int = 10) -> InlineKeyboardMarkup:
	# Encode direction with current page so handler can detect boundaries without double-fetch
	buttons = [
		[
			InlineKeyboardButton(text="صفحه بعدی ⬅️", callback_data=f"financial_page:transactions:next:{page}"),
			InlineKeyboardButton(text="➡️ صفحه قبلی", callback_data=f"financial_page:transactions:prev:{page}"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)


