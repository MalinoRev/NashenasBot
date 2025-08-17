from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_request_location_keyboard() -> InlineKeyboardMarkup:
	rows = [[InlineKeyboardButton(text="📍 ثبت موقعیت GPS", callback_data="nearby:request_location")]]
	return InlineKeyboardMarkup(inline_keyboard=rows)


def get_distance_options() -> list[tuple[str, str]]:
	# (stable_id, label)
	return [
		("nearby_distance:5", "5KM 📍"),
		("nearby_distance:10", "10KM 📍"),
		("nearby_distance:30", "30KM 📍"),
		("nearby_distance:60", "60KM 📍"),
		("nearby_distance:100", "100KM 📍"),
	]


def build_distance_keyboard() -> InlineKeyboardMarkup:
	opts = get_distance_options()
	rows: list[list[InlineKeyboardButton]] = []
	row: list[InlineKeyboardButton] = []
	for idx, (sid, label) in enumerate(opts, start=1):
		row.append(InlineKeyboardButton(text=label, callback_data=sid))
		if idx % 2 == 0 and idx < len(opts):
			rows.append(row)
			row = []
	if row:
		rows.append(row)
	return InlineKeyboardMarkup(inline_keyboard=rows)



