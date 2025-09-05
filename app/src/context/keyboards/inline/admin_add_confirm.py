from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(user_id: int) -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="✅ تایید", callback_data=f"admin_add_confirm:yes:{user_id}"),
				InlineKeyboardButton(text="❌ عدم تایید", callback_data="admin_add_confirm:no")
			]
		]
	)
	return keyboard
