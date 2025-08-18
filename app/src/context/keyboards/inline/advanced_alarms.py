from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_keyboard(visit_on: bool, like_on: bool) -> InlineKeyboardMarkup:
	visit_text = f"🔔 آلارم بازدید پروفایل ({'فعال' if visit_on else 'غیرفعال'})"
	like_text = f"🔔 آلارم لایک پروفایل ({'فعال' if like_on else 'غیرفعال'})"
	rows = [
		[InlineKeyboardButton(text=visit_text, callback_data="advanced_alarms:visit_toggle")],
		[InlineKeyboardButton(text=like_text, callback_data="advanced_alarms:like_toggle")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


