from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="فقط پسرها 👨", callback_data="nearby_gender_5:boys"),
			InlineKeyboardButton(text="فقط دخترها 👩", callback_data="nearby_gender_5:girls"),
		],
		[
			InlineKeyboardButton(text="همه رو نشون بده", callback_data="nearby_gender_5:all"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)



