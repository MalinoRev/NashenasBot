from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text="💬 مشاهده چت‌های فعال", callback_data="chat_management:active"),
		],
		[
			InlineKeyboardButton(text="✅ مشاهده چت‌های اتمام یافته", callback_data="chat_management:completed"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
