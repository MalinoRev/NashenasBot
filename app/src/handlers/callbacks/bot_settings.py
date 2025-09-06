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
		
		await callback.message.answer(await get_branding_message(), reply_markup=build_branding_kb(), parse_mode="Markdown")
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

	# Handle branding settings sub-options
	if data.startswith("bot_settings_branding:"):
		action = data.split(":")[1]
		
		if action == "cache_channel":
			# Handle cache channel setting
			await handle_cache_channel_setting(callback)
			return
		elif action == "name":
			# Handle bot name setting
			await handle_bot_name_setting(callback)
			return
		elif action == "main_channel":
			# Handle main channel setting
			await handle_main_channel_setting(callback)
			return
		elif action == "support_channel":
			# Handle support channel setting
			await handle_support_channel_setting(callback)
			return

	await callback.answer()


async def handle_cache_channel_setting(callback: CallbackQuery) -> None:
	"""Handle cache channel ID setting"""
	async with get_session() as session:
		# Get current user
		user = await session.scalar(
			select(User).where(User.user_id == callback.from_user.id)
		)
		if not user:
			await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
			return
		
		# Get current bot settings
		from src.databases.bot_settings import BotSetting
		settings = await session.scalar(select(BotSetting))
		if not settings:
			await callback.answer("❌ تنظیمات ربات یافت نشد.", show_alert=True)
			return
		
		# Set user step for cache channel input
		user.step = "bot_settings_cache_channel"
		await session.commit()
		
		# Send prompt message
		current_channel = settings.cache_channel_id or "تنظیم نشده"
		await callback.message.edit_text(
			f"💾 تنظیم کانال کش\n\n"
			f"کانال کش فعلی: {current_channel}\n\n"
			f"لطفاً آیدی کانال کش جدید را ارسال کنید:\n"
			f"• آیدی کانال باید عددی باشد\n"
			f"• مثال: -1001234567890\n\n"
			f"برای لغو عملیات /panel_exit را ارسال کنید.",
			reply_markup=None
		)
		
		await callback.answer("📝 آیدی کانال کش را ارسال کنید")


async def handle_bot_name_setting(callback: CallbackQuery) -> None:
	"""Handle bot name setting"""
	await callback.answer("🚧 این قابلیت به زودی اضافه خواهد شد", show_alert=True)


async def handle_main_channel_setting(callback: CallbackQuery) -> None:
	"""Handle main channel setting"""
	await callback.answer("🚧 این قابلیت به زودی اضافه خواهد شد", show_alert=True)


async def handle_support_channel_setting(callback: CallbackQuery) -> None:
	"""Handle support channel setting"""
	await callback.answer("🚧 این قابلیت به زودی اضافه خواهد شد", show_alert=True)
