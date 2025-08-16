from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_rows() -> list[list[tuple[str, str]]]:
	# Each tuple is (stable_id, label)
	return [
		[("main:random_match", "به یه ناشناس وصلم کن! 🔗")],
		[("main:nearby", "افراد نزدیک 📍"), ("main:search", "جستجو کاربران 🕵️")],
		[("main:coin", "سکه 💰"), ("main:profile", "پروفایل 👤"), ("main:help", "راهنما 🤔")],
		[("main:invite", "معرفی به دوستان (سکه رایگان) ⚠️")],
		[("main:my_anon_link", "لینک ناشناس من 📬")],
	]


def build_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	rows_def = get_rows()
	rows: list[list[KeyboardButton]] = []
	text_to_id: dict[str, str] = {}
	for row_def in rows_def:
		row: list[KeyboardButton] = []
		for stable_id, label in row_def:
			row.append(KeyboardButton(text=label))
			text_to_id[label] = stable_id
		rows.append(row)
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	mapping: dict[str, str] = {}
	for row in get_rows():
		for stable_id, label in row:
			mapping[label] = stable_id
	return mapping.get(text)



