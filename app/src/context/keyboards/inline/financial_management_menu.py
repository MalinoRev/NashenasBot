from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows = [
		[InlineKeyboardButton(text="📈 مشاهده آمار کلی درآمد", callback_data="financial:stats")],
		[InlineKeyboardButton(text="📜 مشاهده تراکنش ها", callback_data="financial:transactions")],
		[InlineKeyboardButton(text="🔎 جستجو در پرداختی ها", callback_data="financial:search")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


