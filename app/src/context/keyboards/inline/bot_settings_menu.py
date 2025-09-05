from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="📢 تنظیمات کانال‌های اجباری", callback_data="bot_settings:channels")
			],
			[
				InlineKeyboardButton(text="🎨 تنظیمات برند، کانال و ...", callback_data="bot_settings:branding")
			],
			[
				InlineKeyboardButton(text="🔧 حالت توسعه و تعمیرات", callback_data="bot_settings:maintenance")
			]
		]
	)
	return keyboard
