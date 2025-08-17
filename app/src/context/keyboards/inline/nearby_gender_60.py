from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="فقط پسرها 👨", callback_data="nearby_gender_60:boys"),
			InlineKeyboardButton(text="فقط دخترها 👩", callback_data="nearby_gender_60:girls"),
		],
		[
			InlineKeyboardButton(text="همه رو نشون بده", callback_data="nearby_gender_60:all"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)



