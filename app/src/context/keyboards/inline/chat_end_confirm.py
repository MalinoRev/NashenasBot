from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(chat_id: int) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="بله و اتمام ✅", callback_data=f"chat_end_yes:{chat_id}"),
				InlineKeyboardButton(text="خیر، ادامه چت ❌", callback_data=f"chat_end_no:{chat_id}"),
			]
		]
	)


