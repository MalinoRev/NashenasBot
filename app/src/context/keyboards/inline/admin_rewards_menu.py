from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(
				text="⚙️ تنظیم پاداش تکمیل پروفایل",
				callback_data="admin_rewards:profile_completion"
			)],
			[InlineKeyboardButton(
				text="👥 تنظیم پاداش معرفی دوستان",
				callback_data="admin_rewards:referral"
			)]
		]
	)
	return keyboard
