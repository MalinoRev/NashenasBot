from aiogram import Router
from aiogram.types import CallbackQuery


router = Router(name="callbacks")


@router.callback_query()
async def handle_any_callback(callback: CallbackQuery) -> None:
	await callback.answer()
	await callback.message.answer("Callback received, but not implemented yet.")


