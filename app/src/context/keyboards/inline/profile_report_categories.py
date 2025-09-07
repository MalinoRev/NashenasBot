from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(unique_id: str, categories: list) -> InlineKeyboardMarkup:
	rows: list[list[InlineKeyboardButton]] = []
	for cat in categories:
		label = getattr(cat, "subject", str(cat))
		rows.append([InlineKeyboardButton(text=label, callback_data=f"report_category:{unique_id}:{getattr(cat, 'id', 0)}")])
	# Extra option for non-categorized reports
	rows.append([InlineKeyboardButton(text="سایر موارد", callback_data=f"report_category:{unique_id}:other")])
	return InlineKeyboardMarkup(inline_keyboard=rows)


