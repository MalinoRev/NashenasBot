from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_change_keyboard() -> InlineKeyboardMarkup:
	rows = [[InlineKeyboardButton(text="📍 تغییر موقعیت GPS", callback_data="nearby:request_location")]]
	return InlineKeyboardMarkup(inline_keyboard=rows)


def build_register_keyboard() -> InlineKeyboardMarkup:
	rows = [[InlineKeyboardButton(text="📍 ثبت موقعیت GPS", callback_data="nearby:request_location")]]
	return InlineKeyboardMarkup(inline_keyboard=rows)



