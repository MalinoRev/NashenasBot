from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_rows() -> list[list[tuple[str, str]]]:
	# Each tuple is (stable_id, label)
	return [
		[("admin:user_management", "👥 مدیریت کاربران"), ("admin:chat_management", "💬 مدیریت چت ها")],
		[("admin:financial_management", "💰 مدیریت مالی"), ("admin:reports_management", "📊 مدیریت گزارشات")],
		[("admin:pricing_management", "💳 مدیریت تعرفه ها و محصولات")],
		[("admin:bot_settings", "⚙️ تنظیمات ربات")],
		[("admin:exit", "🚪 خروج از پنل ادمین")],
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
