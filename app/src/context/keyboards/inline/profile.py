from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_profile_keyboard(is_like_active: bool = True) -> InlineKeyboardMarkup:
	like_text = "لایک (فعال ✅)" if is_like_active else "لایک (غیر فعال ⛔️)"
	rows = [
		[
			InlineKeyboardButton(text="مشاهده موقعیت GPS من 📍", callback_data="profile:view_location"),
		],
		[
			InlineKeyboardButton(text=like_text, callback_data="profile:like_toggle"),
			InlineKeyboardButton(text="مشاهده لایک کننده ها ❤️", callback_data="profile:view_likers"),
		],
		[
			InlineKeyboardButton(text="لیست مخاطبین 👩‍🦱👨‍🦱", callback_data="profile:contacts"),
			InlineKeyboardButton(text="بلاک شده ها 🚫", callback_data="profile:blocks"),
		],
		[
			InlineKeyboardButton(text="⚙️ تنظیمات پیشرفته", callback_data="profile:advanced_settings"),
		],
		[
			InlineKeyboardButton(text="ویرایش اطلاعات پروفایل 📝", callback_data="profile:edit"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)



