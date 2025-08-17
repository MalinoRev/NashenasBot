from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_request_location_keyboard() -> InlineKeyboardMarkup:
	rows = [[InlineKeyboardButton(text="📍 ثبت موقعیت GPS", callback_data="nearby:request_location")]]
	return InlineKeyboardMarkup(inline_keyboard=rows)



