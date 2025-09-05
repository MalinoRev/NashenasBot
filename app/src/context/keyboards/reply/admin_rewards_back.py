from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def build_keyboard() -> ReplyKeyboardMarkup:
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="🔙 بازگشت")]
		],
		resize_keyboard=True
	)
	return keyboard


def resolve_id_from_text(text: str) -> str | None:
	if text == "🔙 بازگشت":
		return "admin_rewards:back"
	return None
