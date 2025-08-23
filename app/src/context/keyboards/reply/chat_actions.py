from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def build_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	rows = [
		[
			KeyboardButton(text="پروفایل مخاطب 👤"),
			KeyboardButton(text="چت امن 🔒"),
		],
		[
			KeyboardButton(text="حذف پیام ها 🧹"),
			KeyboardButton(text="پایان چت 🛑"),
		],
	]
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
	text_to_id = {
		"پروفایل مخاطب 👤": "chat:partner_profile",
		"چت امن 🔒": "chat:secure_toggle",
		"حذف پیام ها 🧹": "chat:delete_messages",
		"پایان چت 🛑": "chat:end",
	}
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	mapping = {
		"پروفایل مخاطب 👤": "chat:partner_profile",
		"چت امن 🔒": "chat:secure_toggle",
		"حذف پیام ها 🧹": "chat:delete_messages",
		"پایان چت 🛑": "chat:end",
	}
	return mapping.get(text)


