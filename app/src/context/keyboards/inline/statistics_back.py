from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text="🔙 بازگشت", callback_data="statistics:back"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
