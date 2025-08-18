from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[InlineKeyboardButton(text="❌ لغو", callback_data="profile_edit_photo:cancel")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


