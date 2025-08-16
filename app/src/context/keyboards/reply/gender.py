from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_options() -> list[tuple[str, str]]:
	# (id, label)
	return [
		("gender:female", "🙎‍♀️ دختر"),
		("gender:male", "🙎‍♂️ پسر"),
	]


def build_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	options = get_options()
	rows = [[KeyboardButton(text=label) for _, label in options]]
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)
	text_to_id = {label: id_ for id_, label in options}
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	mapping = {label: id_ for id_, label in get_options()}
	return mapping.get(text)



