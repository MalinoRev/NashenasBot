from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from src.services.nearby_search import generate_nearby_list, GenderFilter
from src.context.keyboards.inline.search_pagination import build_keyboard as build_pagination_kb


async def handle_nearby_gender_100_callback(callback: CallbackQuery) -> None:
	data = callback.data or ""
	gender: GenderFilter = "all"
	if data.endswith(":boys"):
		gender = "boys"
	elif data.endswith(":girls"):
		gender = "girls"
	try:
		await callback.message.delete()
	except Exception:
		pass
	text, ok, has_next, has_items = await generate_nearby_list(callback.from_user.id if callback.from_user else 0, 100, gender, page=1)
	pag_kb: InlineKeyboardMarkup = build_pagination_kb("nearby", page=1, gender=gender, has_next=has_next, max_km=100)
	await callback.message.answer(text, reply_markup=pag_kb, parse_mode="HTML")
	await callback.answer()



