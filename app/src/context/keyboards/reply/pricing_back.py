from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def build_keyboard() -> ReplyKeyboardMarkup:
	"""Build reply keyboard for pricing management back button."""
	rows: list[list[KeyboardButton]] = [
		[KeyboardButton(text="🔙 بازگشت")],
	]
	return ReplyKeyboardMarkup(
		keyboard=rows,
		resize_keyboard=True,
		one_time_keyboard=False,
	)
