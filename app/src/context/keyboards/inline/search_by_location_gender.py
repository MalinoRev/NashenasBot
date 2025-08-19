from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows: list[list[InlineKeyboardButton]] = []
	rows.append([InlineKeyboardButton(text="🌐 همه", callback_data="search_by_location_gender:all")])
	rows.append([
		InlineKeyboardButton(text="👧 فقط دختر ها", callback_data="search_by_location_gender:female"),
		InlineKeyboardButton(text="👦 فقط پسر ها", callback_data="search_by_location_gender:male"),
	])
	return InlineKeyboardMarkup(inline_keyboard=rows)


