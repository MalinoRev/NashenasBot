from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(prices: list[tuple[int, int, int]], vip_price: int | None = None) -> InlineKeyboardMarkup:
	"""
	prices: list of tuples (price_id, amount, price)
	"""
	rows: list[list[InlineKeyboardButton]] = []
	for price_id, amount, price in prices:
		# Add some emojis to make it attractive
		label = f"💳 {price:,} تومان — 🪙 {amount} سکه"
		rows.append([InlineKeyboardButton(text=label, callback_data=f"coin:buy:{price_id}")])
	# Append VIP rank purchase button at the end
	if (vip_price or 0) > 0:
		rows.append([InlineKeyboardButton(text=f"👑 خرید رنک ویژه  — {vip_price:,} تومان", callback_data="coin:buy_vip")])
	return InlineKeyboardMarkup(inline_keyboard=rows)


