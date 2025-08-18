from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard() -> InlineKeyboardMarkup:
	rows = []
	# All option
	rows.append([InlineKeyboardButton(text="👥 همه", callback_data="advanced_filter_age_from:all")])
	# Age 1..99 in rows of 6
	row: list[InlineKeyboardButton] = []
	for age in range(1, 100):
		row.append(InlineKeyboardButton(text=str(age), callback_data=f"advanced_filter_age_from:{age}"))
		if len(row) == 6:
			rows.append(row)
			row = []
	if row:
		rows.append(row)
	return InlineKeyboardMarkup(inline_keyboard=rows)


