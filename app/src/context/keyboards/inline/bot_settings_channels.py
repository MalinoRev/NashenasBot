from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="➕ اضافه کردن کانال", callback_data="bot_settings_channels:add")
			],
			[
				InlineKeyboardButton(text="📝 ویرایش کانال‌ها", callback_data="bot_settings_channels:edit")
			],
			[
				InlineKeyboardButton(text="🔙 بازگشت", callback_data="bot_settings:back")
			]
		]
	)
	return keyboard
