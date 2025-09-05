from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
	rows = [
		[
			InlineKeyboardButton(text="✅ تایید حذف", callback_data=f"support_remove_confirm:yes:{target_user_id}"),
			InlineKeyboardButton(text="❌ عدم تایید", callback_data="support_remove_confirm:no"),
		]
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


