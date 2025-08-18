from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard(min_age: int | None) -> InlineKeyboardMarkup:
	rows = []
	rows.append([InlineKeyboardButton(text="👥 همه", callback_data="advanced_filter_age_until:all")])
	start = (min_age or 1)
	row: list[InlineKeyboardButton] = []
	for age in range(start, 100):
		row.append(InlineKeyboardButton(text=str(age), callback_data=f"advanced_filter_age_until:{age}"))
		if len(row) == 6:
			rows.append(row)
			row = []
	if row:
		rows.append(row)
	return InlineKeyboardMarkup(inline_keyboard=rows)


