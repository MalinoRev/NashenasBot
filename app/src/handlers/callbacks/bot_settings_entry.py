from aiogram.types import Message
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select
import os


async def show_bot_settings(message: Message) -> None:
	# Check if user is admin
	user_id = message.from_user.id if message.from_user else 0
	is_admin = False
	try:
		admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
		if user_id and admin_env and str(user_id) == str(admin_env):
			is_admin = True
		else:
			if user_id:
				from src.databases.admins import Admin
				async with get_session() as session:
					user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
					if user is not None:
						exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
						is_admin = bool(exists)
	except Exception:
		is_admin = False

	if not is_admin:
		await message.answer("❌ شما دسترسی به این بخش ندارید.")
		return

	# Ensure step is admin_panel
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_panel":
			await message.answer("❌ شما در پنل مدیریت نیستید.")
			return

	from src.context.messages.replies.bot_settings_welcome import get_message as get_settings_message
	from src.context.keyboards.inline.bot_settings_menu import build_keyboard as build_settings_kb

	await message.answer(get_settings_message(), reply_markup=build_settings_kb(), parse_mode="Markdown")
