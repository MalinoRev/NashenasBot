from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(unique_id: str) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(text="ارسال پیام دایرکت ✉️", callback_data=f"direct_confirm:{unique_id}")]
		]
	)


