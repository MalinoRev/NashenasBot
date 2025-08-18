from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[InlineKeyboardButton(text="👥 همه", callback_data="advanced_filter_distance:all")],
		[
			InlineKeyboardButton(text="🧭 هم استانی باشه", callback_data="advanced_filter_distance:same_state"),
			InlineKeyboardButton(text="🧭 هم استانی نباشه 🚫", callback_data="advanced_filter_distance:not_same_state"),
		],
		[
			InlineKeyboardButton(text="🏙️ هم شهری باشه", callback_data="advanced_filter_distance:same_city"),
			InlineKeyboardButton(text="🏙️ هم شهری نباشه 🚫", callback_data="advanced_filter_distance:not_same_city"),
		],
		[
			InlineKeyboardButton(text="📍 نزدیک تر از 100 کیلومتر", callback_data="advanced_filter_distance:lt_100"),
			InlineKeyboardButton(text="📍 نزدیک تر از 10 کیلومتر", callback_data="advanced_filter_distance:lt_10"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


