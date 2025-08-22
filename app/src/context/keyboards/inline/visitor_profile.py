from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(*, unique_id: str, liked: bool, likes_count: int, is_blocked: bool, in_contacts: bool) -> InlineKeyboardMarkup:
	like_emoji = "❤️" if liked else "🤍"
	rows: list[list[InlineKeyboardButton]] = []
	rows.append([InlineKeyboardButton(text=f"{like_emoji} {likes_count}", callback_data=f"profile_like:{unique_id}")])
	rows.append([
		InlineKeyboardButton(text="درخواست چت", callback_data=f"profile_chat_request:{unique_id}"),
		InlineKeyboardButton(text="پیام دایرکت", callback_data=f"profile_direct:{unique_id}"),
	])
	block_text = "آن‌بلاک کردن کاربر" if is_blocked else "بلاک کردن کاربر"
	contacts_text = "حذف از مخاطبین" if in_contacts else "افزودن به مخاطبین"
	rows.append([
		InlineKeyboardButton(text=block_text, callback_data=f"profile_block_toggle:{unique_id}"),
		InlineKeyboardButton(text=contacts_text, callback_data=f"profile_contact_toggle:{unique_id}"),
	])
	rows.append([
		InlineKeyboardButton(text="گزارش کاربر", callback_data=f"profile_report:{unique_id}"),
	])
	return InlineKeyboardMarkup(inline_keyboard=rows)


