from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from src.services.new_users_search import generate_new_users_list, GenderFilter
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb
from src.context.keyboards.inline.search_pagination import build_keyboard as build_pagination_kb


async def handle_search_new_users(callback: CallbackQuery) -> None:
	data = callback.data or ""
	gender: GenderFilter = "all"
	if data.endswith(":male"):
		gender = "boys"
	elif data.endswith(":female"):
		gender = "girls"
	try:
		await callback.message.delete()
	except Exception:
		pass
	text, ok, has_next, has_items = await generate_new_users_list(callback.from_user.id if callback.from_user else 0, gender, page=1)
	pag_kb: InlineKeyboardMarkup = build_pagination_kb("new_users", page=1, gender=gender, has_next=has_next)
	await callback.message.answer(text, reply_markup=pag_kb, parse_mode="HTML")
	await callback.answer()


