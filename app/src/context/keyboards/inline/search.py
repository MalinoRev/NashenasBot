from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	rows: list[list[InlineKeyboardButton]] = []
	rows.append([
		InlineKeyboardButton(text="💌 به مخاطب خاصم وصلم کن", callback_data="search:special_contact"),
	])
	rows.append([
		InlineKeyboardButton(text="🏛️ هم استانی", callback_data="search:same_province"),
		InlineKeyboardButton(text="🧑‍🎓 هم سن ها", callback_data="search:same_age"),
	])
	# rows.append([
	# 	InlineKeyboardButton(text="🛠️ جستجو پیشرفته", callback_data="search:advanced"),
	# ])
	rows.append([
		InlineKeyboardButton(text="🆕 کاربران جدید", callback_data="search:new_users"),
		InlineKeyboardButton(text="🚫 بدون چت ها", callback_data="search:no_chats"),
	])
	rows.append([
		InlineKeyboardButton(text="🕘 چت های اخیر من", callback_data="search:recent_chats"),
	])
	rows.append([
		InlineKeyboardButton(text="📍 جستجو با موقعیت مکانی", callback_data="search:by_location"),
	])
	rows.append([
		InlineKeyboardButton(text="⭐ کاربران محبوب بر اساس لایک", callback_data="search:popular"),
	])
	return InlineKeyboardMarkup(inline_keyboard=rows)


