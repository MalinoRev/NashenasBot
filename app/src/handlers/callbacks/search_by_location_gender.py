from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.search_by_location_gender import get_message as get_gender_message
from src.context.keyboards.inline.search_by_location_gender import build_keyboard as build_gender_kb


async def handle_search_by_location_gender_prompt(callback: CallbackQuery) -> None:
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(get_gender_message(), reply_markup=build_gender_kb())
	await callback.answer()


