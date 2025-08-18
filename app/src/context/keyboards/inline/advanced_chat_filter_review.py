from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="✅ نمایش متن", callback_data="advanced_filter_review:show"),
			InlineKeyboardButton(text="🚫 عدم نمایش متن", callback_data="advanced_filter_review:hide"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


