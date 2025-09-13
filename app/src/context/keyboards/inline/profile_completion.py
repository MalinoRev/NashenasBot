from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows: list[list[InlineKeyboardButton]] = [
		[InlineKeyboardButton(text="✅ تکمیل پروفایل", callback_data="profile_completion:start")]
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


