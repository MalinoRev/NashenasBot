from aiogram.types import CallbackQuery, LinkPreviewOptions
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.commands.start import get_message as get_start_message
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb, build_keyboard_for


async def handle_profile_edit_photo_cancel(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return
		user.step = "start"
		await session.commit()

	# Delete the prompt message
	try:
		await callback.message.delete()
	except Exception:
		pass

	name = (callback.from_user.first_name if callback.from_user else None) or (callback.from_user.username if callback.from_user else None)
	start_text = get_start_message(name)
	kb, _ = await build_keyboard_for(callback.from_user.id if callback.from_user else None)
	await callback.message.answer(start_text, reply_markup=kb, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True))
	await callback.answer()


