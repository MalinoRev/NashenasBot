from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_options() -> list[tuple[str, str]]:
	# (stable_id, label)
	return [
		("special:back", "بازگشت 🔙"),
	]


def build_back_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	options = get_options()
	rows = []
	for stable_id, label in options:
		btn = KeyboardButton(text=label)
		rows.append([btn])
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)
	text_to_id = {label: stable_id for stable_id, label in options}
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	mapping = {label: stable_id for stable_id, label in get_options()}
	return mapping.get(text)


