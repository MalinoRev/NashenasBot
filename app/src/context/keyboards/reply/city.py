from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Iterable


def build_keyboard(city_names: Iterable[str]) -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	# Map labels to stable ids: city:<name>
	rows: list[list[KeyboardButton]] = []
	row: list[KeyboardButton] = []
	text_to_id: dict[str, str] = {}
	for name in city_names:
		label = name
		id_ = f"city:{name}"
		text_to_id[label] = id_
		row.append(KeyboardButton(text=label))
		if len(row) == 3:
			rows.append(row)
			row = []
	if row:
		rows.append(row)
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str:
	return f"city:{text}"



