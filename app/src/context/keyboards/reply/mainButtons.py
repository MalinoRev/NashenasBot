from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_rows() -> list[list[tuple[str, str]]]:
	# Each tuple is (stable_id, label)
	return [
		[("main:random_match", "به یه ناشناس وصلم کن! 🔗")],
		[("main:search", "جستجو کاربران 🕵️"), ("main:nearby", "افراد نزدیک 📍")],
		[("main:coin", "سکه 💰"), ("main:profile", "پروفایل 👤"), ("main:help", "راهنما 🤔")],
		[("main:invite", "معرفی به دوستان (سکه رایگان) ⚠️")],
		[("main:my_anon_link", "لینک ناشناس من 📬")],
	]


async def build_keyboard_for(user_telegram_id: int | None) -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	rows_def = get_rows()
	# Conditionally append admin panel row
	is_admin = False
	try:
		import os
		from sqlalchemy import select
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.admins import Admin
		admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
		if user_telegram_id and admin_env and str(user_telegram_id) == str(admin_env):
			is_admin = True
		else:
			if user_telegram_id:
				async with get_session() as session:
					user: User | None = await session.scalar(select(User).where(User.user_id == user_telegram_id))
					if user is not None:
						exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
						is_admin = bool(exists)
	except Exception:
		is_admin = False
	if is_admin:
		rows_def = rows_def + [[("admin:panel", "پنل ادمین 🛠️")]]

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


def build_keyboard() -> tuple[ReplyKeyboardMarkup, dict[str, str]]:
	# Backward-compatible builder when user id is unknown (no admin row)
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
	# Also map admin label if present
	mapping["پنل ادمین 🛠️"] = "admin:panel"
	return mapping.get(text)



