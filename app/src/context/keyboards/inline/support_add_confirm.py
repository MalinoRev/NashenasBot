from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="✅ تایید", callback_data=f"support_add_confirm:yes:{target_user_id}"),
			InlineKeyboardButton(text="❌ عدم تایید", callback_data="support_add_confirm:no"),
		]
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


