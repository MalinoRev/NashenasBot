from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(user_id: int) -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="✅ تایید حذف", callback_data=f"admin_remove_confirm:yes:{user_id}"),
				InlineKeyboardButton(text="❌ عدم تایید", callback_data="admin_remove_confirm:no")
			]
		]
	)
	return keyboard
