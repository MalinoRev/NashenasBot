from aiogram.types import CallbackQuery

from src.context.messages.callbacks.profile_advanced_settings import (
	get_message as get_advanced_msg,
)
from src.context.keyboards.inline.profile_advanced_settings import (
	build_keyboard as build_advanced_kb,
)


async def handle_profile_advanced_settings(callback: CallbackQuery) -> None:
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_advanced_msg(), reply_markup=build_advanced_kb())
	await callback.answer()


