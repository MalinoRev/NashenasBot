from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_options() -> list[tuple[str, str]]:
	# (stable_id, label)
	return [
		("special:back", "بازگشت 🔙"),
	]


def build_back_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	print("LOG: build_back_keyboard called")
	options = get_options()
	print(f"LOG: Options: {options}")
	rows = []
	for stable_id, label in options:
		btn = KeyboardButton(text=label)
		rows.append([btn])
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)
	text_to_id = {label: stable_id for stable_id, label in options}
	print(f"LOG: Back keyboard built with {len(rows)} rows, text_to_id: {text_to_id}")
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	print(f"LOG: resolve_id_from_text called with text: '{text}'")
	mapping = {label: stable_id for stable_id, label in get_options()}
	result = mapping.get(text)
	print(f"LOG: resolve_id_from_text result: '{result}' (mapping: {mapping})")
	return result


