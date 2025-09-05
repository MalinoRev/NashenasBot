from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="➕ اضافه کردن ادمین", callback_data="admin_management:add"),
				InlineKeyboardButton(text="➖ حذف ادمین", callback_data="admin_management:remove")
			]
		]
	)
	return keyboard
