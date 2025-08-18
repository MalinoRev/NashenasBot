from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.profileMiddleware.enterPhoto import get_message as get_enter_photo_message
from src.context.keyboards.inline.profile_edit_photo_cancel import build_keyboard as build_cancel_kb


async def handle_profile_edit_photo(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return
		# Set user step to edit_photo
		user.step = "edit_photo"
		await session.commit()

	# Delete previous message
	try:
		await callback.message.delete()
	except Exception:
		pass

	# Remove any existing reply keyboard using a visible temporary message, then delete it
	tmp_msg = None
	try:
		tmp_msg = await callback.message.answer("…", reply_markup=ReplyKeyboardRemove())
	except Exception:
		pass

	await callback.message.answer(get_enter_photo_message(), reply_markup=build_cancel_kb())

	# Clean up the temporary removal message to keep chat tidy
	if tmp_msg is not None:
		try:
			await tmp_msg.delete()
		except Exception:
			pass
	await callback.answer()


