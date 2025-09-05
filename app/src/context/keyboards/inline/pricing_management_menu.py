from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	"""Build inline keyboard for pricing management menu."""
	rows: list[list[InlineKeyboardButton]] = [
		[InlineKeyboardButton(text="👑 تنظیم تعرفه رنک VIP", callback_data="pricing:vip_price")],
		[InlineKeyboardButton(text="⏰ تنظیم زمان رنک VIP", callback_data="pricing:vip_time")],
		[InlineKeyboardButton(text="🗑️ تنظیم تعرفه حذف اکانت", callback_data="pricing:delete_price")],
		[InlineKeyboardButton(text="🔓 تنظیم تعرفه رفع مسدودیت", callback_data="pricing:unban_price")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)
