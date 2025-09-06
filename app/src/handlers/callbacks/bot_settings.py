from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select
import os


async def handle_bot_settings(callback: CallbackQuery) -> None:
	data = callback.data or ""
	# Accept both main and branding namespace callbacks
	is_main = data.startswith("bot_settings:")
	is_branding = data.startswith("bot_settings_branding:")
	if not (is_main or is_branding):
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

	# Relax step requirement: allow handling as long as user exists
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
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
		from src.context.keyboards.reply.bot_settings_back import build_keyboard as build_back_kb
		kb = build_back_kb()
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(
			f"💾 تنظیم کانال کش\n\n"
			f"کانال کش فعلی: {current_channel}\n\n"
			f"لطفاً آیدی کانال کش جدید را ارسال کنید:\n"
			f"• آیدی کانال باید عددی باشد\n"
			f"• مثال: -1001234567890\n\n"
			f"برای لغو، از دکمه بازگشت استفاده کنید.",
			reply_markup=kb
		)
		
		await callback.answer("📝 آیدی کانال کش را ارسال کنید")


async def handle_bot_name_setting(callback: CallbackQuery) -> None:
	"""Handle bot name setting: set step and prompt for new name"""
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

		# Set user step for bot name input
		user.step = "bot_settings_bot_name"
		await session.commit()

		# Send prompt message
		current_name = settings.bot_name or "تنظیم نشده"
		from src.context.keyboards.reply.bot_settings_back import build_keyboard as build_back_kb
		kb = build_back_kb()
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(
			f"📝 تنظیم نام ربات\n\n"
			f"نام فعلی ربات: {current_name}\n\n"
			f"لطفاً نام جدید ربات را ارسال کنید:\n"
			f"• حداکثر 255 کاراکتر\n"
			f"• مثال: NashenasBot\n\n"
			f"برای لغو، از دکمه بازگشت استفاده کنید.",
			reply_markup=kb
		)

		await callback.answer("📝 نام جدید ربات را ارسال کنید")


async def handle_main_channel_setting(callback: CallbackQuery) -> None:
	"""Handle main channel setting: set step and prompt for username"""
	async with get_session() as session:
		user = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user:
			await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
			return
		from src.databases.bot_settings import BotSetting
		settings = await session.scalar(select(BotSetting))
		if not settings:
			await callback.answer("❌ تنظیمات ربات یافت نشد.", show_alert=True)
			return
		user.step = "bot_settings_main_channel"
		await session.commit()
		current_channel = settings.bot_channel or "تنظیم نشده"
		from src.context.keyboards.reply.bot_settings_back import build_keyboard as build_back_kb
		kb = build_back_kb()
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(
			f"📢 تنظیم کانال اصلی\n\n"
			f"کانال اصلی فعلی: {current_channel}\n\n"
			f"لطفاً نام کاربری کانال اصلی را ارسال کنید:\n"
			f"• بدون @ در ابتدا\n"
			f"• فقط حروف، اعداد و زیرخط (5 تا 32 کاراکتر)\n"
			f"• مثال: nashenas_channel\n\n"
			f"برای لغو، از دکمه بازگشت استفاده کنید.",
			reply_markup=kb
		)
		await callback.answer("📝 نام کاربری کانال اصلی را ارسال کنید")


async def handle_support_channel_setting(callback: CallbackQuery) -> None:
	"""Handle support channel setting: set step and prompt for username"""
	async with get_session() as session:
		user = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user:
			await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
			return
		from src.databases.bot_settings import BotSetting
		settings = await session.scalar(select(BotSetting))
		if not settings:
			await callback.answer("❌ تنظیمات ربات یافت نشد.", show_alert=True)
			return
		user.step = "bot_settings_support_channel"
		await session.commit()
		current_support = settings.bot_support_username or "تنظیم نشده"
		from src.context.keyboards.reply.bot_settings_back import build_keyboard as build_back_kb
		kb = build_back_kb()
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(
			f"🆘 تنظیم کانال پشتیبانی\n\n"
			f"کانال پشتیبانی فعلی: {current_support}\n\n"
			f"لطفاً نام کاربری کانال پشتیبانی را ارسال کنید:\n"
			f"• بدون @ در ابتدا\n"
			f"• فقط حروف، اعداد و زیرخط (5 تا 32 کاراکتر)\n"
			f"• مثال: nashenas_support\n\n"
			f"برای لغو، از دکمه بازگشت استفاده کنید.",
			reply_markup=kb
		)
		await callback.answer("📝 نام کاربری کانال پشتیبانی را ارسال کنید")
