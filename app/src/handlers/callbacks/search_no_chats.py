from aiogram.types import CallbackQuery

from src.services.no_chats_search import generate_no_chats_list, GenderFilter


async def handle_search_no_chats(callback: CallbackQuery) -> None:
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
	text, ok = await generate_no_chats_list(callback.from_user.id if callback.from_user else 0, gender)
	await callback.message.answer(text)
	await callback.answer()


