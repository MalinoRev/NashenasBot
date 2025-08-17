from aiogram import Router
from aiogram.types import CallbackQuery


router = Router(name="callbacks")


@router.callback_query()
async def handle_any_callback(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if data == "random_match:random":
		from src.handlers.callbacks.random_match import handle_random_match_callback
		await handle_random_match_callback(callback)
		return
	if data == "random_match:male":
		from src.handlers.callbacks.random_match_male import handle_random_match_male_callback
		await handle_random_match_male_callback(callback)
		return
	await callback.answer()
	await callback.message.answer("Callback received, but not implemented yet.")


