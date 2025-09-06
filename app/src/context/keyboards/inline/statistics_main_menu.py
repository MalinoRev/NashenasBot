from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text="📈 جدول آمار", callback_data="statistics:table"),
		],
		[
			InlineKeyboardButton(text="📊 جدول مقایسه", callback_data="statistics:comparison"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
