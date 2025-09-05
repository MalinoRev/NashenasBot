from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="📝 ویرایش نام ربات", callback_data="bot_settings_branding:name"),
				InlineKeyboardButton(text="📝 ویرایش توضیحات", callback_data="bot_settings_branding:description")
			],
			[
				InlineKeyboardButton(text="📢 تنظیم کانال اصلی", callback_data="bot_settings_branding:main_channel"),
				InlineKeyboardButton(text="🆘 تنظیم کانال پشتیبانی", callback_data="bot_settings_branding:support_channel")
			],
			[
				InlineKeyboardButton(text="🔙 بازگشت", callback_data="bot_settings:back")
			]
		]
	)
	return keyboard
