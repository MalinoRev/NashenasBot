from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(report_id: int) -> InlineKeyboardMarkup:
	rows: list[list[InlineKeyboardButton]] = [
		[
			InlineKeyboardButton(text="✅ تایید", callback_data=f"report_approve:{report_id}"),
			InlineKeyboardButton(text="✅ تایید و مجازات", callback_data=f"report_approve_punish:{report_id}"),
		],
		[InlineKeyboardButton(text="❌ عدم تایید", callback_data=f"report_reject:{report_id}")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)

