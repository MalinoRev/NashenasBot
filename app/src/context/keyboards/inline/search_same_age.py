from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows: list[list[InlineKeyboardButton]] = []
	rows.append([InlineKeyboardButton(text="🌐 همه", callback_data="search_same_age:all")])
	rows.append([
		InlineKeyboardButton(text="👧 فقط دختر ها", callback_data="search_same_age:female"),
		InlineKeyboardButton(text="👦 فقط پسر ها", callback_data="search_same_age:male"),
	])
	return InlineKeyboardMarkup(inline_keyboard=rows)


