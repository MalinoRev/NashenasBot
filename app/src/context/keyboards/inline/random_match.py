from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_searching_keyboard() -> InlineKeyboardMarkup:
	# Single button with stable callback id
	rows = [
		[
			InlineKeyboardButton(
				text="❌ لغو و بازگشت ❌",
				callback_data="random_match:cancel",
			)
		]
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)



