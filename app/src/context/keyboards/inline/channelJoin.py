from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(channel_usernames: List[str]) -> InlineKeyboardMarkup:
	buttons: List[List[InlineKeyboardButton]] = []
	for idx, username in enumerate(channel_usernames, start=1):
		label = f"کانال اجباری {idx}"
		url = f"https://t.me/{username}"
		buttons.append([InlineKeyboardButton(text=label, url=url)])
	# Final check button
	buttons.append([InlineKeyboardButton(text="بررسی عضویت ✅", callback_data="check_channels_membership")])
	return InlineKeyboardMarkup(inline_keyboard=buttons)
