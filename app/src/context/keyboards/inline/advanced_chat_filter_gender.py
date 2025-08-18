from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard() -> InlineKeyboardMarkup:
	# IDs are stable and independent of texts
	rows = [
		[InlineKeyboardButton(text="👥 همه کاربران", callback_data="advanced_filter_gender:all")],
		[
			InlineKeyboardButton(text="👧 فقط دختر ها", callback_data="advanced_filter_gender:female"),
			InlineKeyboardButton(text="👦 فقط پسر ها", callback_data="advanced_filter_gender:male"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


