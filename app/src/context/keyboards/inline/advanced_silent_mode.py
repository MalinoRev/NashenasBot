from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(is_active: bool = False) -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="سایلنت تا 30 دقیقه 🔔", callback_data="advanced_silent:30m"),
			InlineKeyboardButton(text="سایلنت تا یک ساعت 🔔", callback_data="advanced_silent:1h"),
		],
		[
			InlineKeyboardButton(text="همیشه سایلنت 🔔", callback_data="advanced_silent:forever"),
		],
	]
	if is_active:
		rows.append([InlineKeyboardButton(text="خاموش کردن سایلنت 🔕", callback_data="advanced_silent:off")])
	return InlineKeyboardMarkup(inline_keyboard=rows)


