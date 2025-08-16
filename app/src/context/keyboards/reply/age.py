from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_options() -> list[tuple[str, str]]:
	# Use string IDs to decouple from labels
	return [(f"age:{n}", str(n)) for n in range(1, 100)]


def build_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	options = get_options()
	rows: list[list[KeyboardButton]] = []
	row: list[KeyboardButton] = []
	for _, label in options:
		row.append(KeyboardButton(text=label))
		if len(row) == 10:
			rows.append(row)
			row = []
	if row:
		rows.append(row)
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
	text_to_id = {label: id_ for id_, label in options}
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	mapping = {label: id_ for id_, label in get_options()}
	return mapping.get(text)



