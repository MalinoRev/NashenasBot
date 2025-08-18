from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [[InlineKeyboardButton(text="💳 پرداخت", callback_data="advanced_delete:pay")]]
	return InlineKeyboardMarkup(inline_keyboard=rows)


