from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="📝 تغییر جنسیت", callback_data="profile_edit:gender"),
			InlineKeyboardButton(text="📝 تغییر نام", callback_data="profile_edit:name"),
		],
		[
			InlineKeyboardButton(text="📝 تغییر سن", callback_data="profile_edit:age"),
			InlineKeyboardButton(text="📝 تغییر عکس", callback_data="profile_edit:photo"),
		],
		[
			InlineKeyboardButton(text="📝 تغییر استان و شهر", callback_data="profile_edit:state_city"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


