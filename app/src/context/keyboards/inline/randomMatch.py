from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🎲 جستجوی شانسی", callback_data="random_match:random")],
		[
			InlineKeyboardButton(text="🙍‍♂️ جستجوی پسر", callback_data="random_match:male"),
			InlineKeyboardButton(text="🙍‍♀️ جستجوی دختر", callback_data="random_match:female"),
		],
		[InlineKeyboardButton(text="🛰 جستجوی اطراف", callback_data="random_match:nearby")],
		[InlineKeyboardButton(text="🌐 جستجو بر پایه استان 🎯", callback_data="random_match:state")],
	])
