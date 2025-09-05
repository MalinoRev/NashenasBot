from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select
import os


async def handle_bot_settings(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("bot_settings:"):
		await callback.answer()
		return

	user_id = callback.from_user.id if callback.from_user else 0
	# Check if user is admin
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
		await callback.answer("❌ شما دسترسی به این بخش ندارید.", show_alert=True)
		return

	# Check user step
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_panel":
			await callback.answer("❌ شما در پنل مدیریت نیستید.", show_alert=True)
			return

	# Handle different bot settings options
	if data == "bot_settings:channels":
		from src.context.messages.replies.bot_settings_channels import get_message as get_channels_message
		from src.context.keyboards.inline.bot_settings_channels import build_keyboard as build_channels_kb
		
		try:
			await callback.message.delete()
		except Exception:
			pass
		
		await callback.message.answer(get_channels_message(), reply_markup=build_channels_kb(), parse_mode="Markdown")
		await callback.answer()
		return

	if data == "bot_settings:branding":
		from src.context.messages.replies.bot_settings_branding import get_message as get_branding_message
		from src.context.keyboards.inline.bot_settings_branding import build_keyboard as build_branding_kb
		
		try:
			await callback.message.delete()
		except Exception:
			pass
		
		await callback.message.answer(get_branding_message(), reply_markup=build_branding_kb(), parse_mode="Markdown")
		await callback.answer()
		return

	if data == "bot_settings:maintenance":
		from src.context.messages.replies.bot_settings_maintenance import get_message as get_maintenance_message
		from src.context.keyboards.inline.bot_settings_maintenance import build_keyboard as build_maintenance_kb
		
		try:
			await callback.message.delete()
		except Exception:
			pass
		
		await callback.message.answer(get_maintenance_message(), reply_markup=build_maintenance_kb(), parse_mode="Markdown")
		await callback.answer()
		return

	if data == "bot_settings:back":
		# Return to main bot settings
		from src.context.messages.replies.bot_settings_welcome import get_message as get_settings_message
		from src.context.keyboards.inline.bot_settings_menu import build_keyboard as build_settings_kb
		
		try:
			await callback.message.delete()
		except Exception:
			pass
		
		await callback.message.answer(get_settings_message(), reply_markup=build_settings_kb(), parse_mode="Markdown")
		await callback.answer()
		return

	await callback.answer()
