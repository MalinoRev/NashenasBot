from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text="🚫 مدیریت کاربران مسدود شده", callback_data="user_management:banned"),
		],
		[
			InlineKeyboardButton(text="🔍 جستجو کاربر", callback_data="user_management:search"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
