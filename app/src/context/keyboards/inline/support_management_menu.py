from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="➕ اضافه کردن پشتیبان", callback_data="support_management:add"),
				InlineKeyboardButton(text="➖ حذف پشتیبان", callback_data="support_management:remove")
			]
		]
	)
	return keyboard


