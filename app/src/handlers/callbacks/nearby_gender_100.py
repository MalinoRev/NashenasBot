from aiogram.types import CallbackQuery

from src.services.nearby_search import generate_nearby_list, GenderFilter


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
	text, ok = await generate_nearby_list(callback.from_user.id if callback.from_user else 0, 100, gender)
	await callback.message.answer(text)
	await callback.answer()



