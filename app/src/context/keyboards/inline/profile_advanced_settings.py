from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	# Stable IDs for each setting action
	rows = [
		[InlineKeyboardButton(text="حالت سایلنت 🔔", callback_data="advanced:silent_mode")],
		[InlineKeyboardButton(text="فیلتر درخواست چت ⚖️", callback_data="advanced:chat_filter")],
		[InlineKeyboardButton(text="❌ حذف حساب کاربری ❌", callback_data="advanced:delete_account")],
		[InlineKeyboardButton(text="🔔 تنظیم آلارم ها ⚙️", callback_data="advanced:alarms")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


