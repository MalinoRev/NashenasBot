from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_options() -> list[tuple[str, str, bool]]:
	# (stable_id, label, request_location)
	return [
		("nearby:send_location", "ارسال موقعیت کنونی", True),
		("nearby:back", "بازگشت 🔙", False),
	]


def build_send_location_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	options = get_options()
	rows = []
	for stable_id, label, req_loc in options:
		btn = KeyboardButton(text=label, request_location=req_loc)
		rows.append([btn]) if req_loc else rows.append([btn])
	kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)
	text_to_id = {label: stable_id for stable_id, label, _ in options}
	return kb, text_to_id


def resolve_id_from_text(text: str) -> str | None:
	mapping = {label: stable_id for stable_id, label, _ in get_options()}
	return mapping.get(text)



