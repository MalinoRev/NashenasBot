from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(prices: list[tuple[int, int, int]]) -> InlineKeyboardMarkup:
	"""
	prices: list of tuples (price_id, amount, price)
	"""
	rows: list[list[InlineKeyboardButton]] = []
	for price_id, amount, price in prices:
		# Add some emojis to make it attractive
		label = f"💳 {price:,} تومان — 🪙 {amount} سکه"
		rows.append([InlineKeyboardButton(text=label, callback_data=f"coin:buy:{price_id}")])
	return InlineKeyboardMarkup(inline_keyboard=rows)


