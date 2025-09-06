from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_keyboard() -> ReplyKeyboardMarkup:
	buttons = [
		[KeyboardButton(text="🔙 بازگشت")],
	]
	return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
