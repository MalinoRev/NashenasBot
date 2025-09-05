from aiogram.types import CallbackQuery

from src.context.keyboards.inline.advanced_delete_account import build_keyboard
from src.context.messages.callbacks.advanced_delete_account import get_message


async def handle_advanced_delete_account(callback: CallbackQuery) -> None:
	try:
		await callback.message.delete()
	except Exception:
		pass
	text = await get_message()
	await callback.message.answer(text, reply_markup=build_keyboard())
	await callback.answer()


