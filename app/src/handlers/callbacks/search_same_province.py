from aiogram.types import CallbackQuery

from src.services.state_search import generate_state_list, GenderFilter


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
	text, ok = await generate_state_list(callback.from_user.id if callback.from_user else 0, gender)
	await callback.message.answer(text)
	await callback.answer()


