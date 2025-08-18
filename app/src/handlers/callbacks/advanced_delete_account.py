from aiogram.types import CallbackQuery

from src.context.messages.callbacks.advanced_delete_account import get_message
from src.context.keyboards.inline.advanced_delete_account import build_keyboard


async def handle_advanced_delete_account(callback: CallbackQuery) -> None:
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_message(), reply_markup=build_keyboard())
	await callback.answer()


