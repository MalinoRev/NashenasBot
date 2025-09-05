from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="🟢 فعال کردن حالت عادی", callback_data="bot_settings_maintenance:normal")
			],
			[
				InlineKeyboardButton(text="🔧 فعال کردن حالت تعمیرات", callback_data="bot_settings_maintenance:maintenance")
			],
			[
				InlineKeyboardButton(text="🔙 بازگشت", callback_data="bot_settings:back")
			]
		]
	)
	return keyboard
