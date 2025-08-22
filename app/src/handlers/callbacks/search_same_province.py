from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from src.services.state_search import generate_state_list, GenderFilter
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb, build_keyboard_for
from src.context.keyboards.inline.search_pagination import build_keyboard as build_pagination_kb


async def handle_search_same_province(callback: CallbackQuery) -> None:
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
	text, ok, has_next, has_items = await generate_state_list(callback.from_user.id if callback.from_user else 0, gender, page=1)
	main_kb, _ = await build_keyboard_for(callback.from_user.id if callback.from_user else None)
	pag_kb: InlineKeyboardMarkup = build_pagination_kb("same_province", page=1, gender=gender, has_next=has_next)
	await callback.message.answer(text, reply_markup=pag_kb, parse_mode="HTML")
	await callback.answer()


