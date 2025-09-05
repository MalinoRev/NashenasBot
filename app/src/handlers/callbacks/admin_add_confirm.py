from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from src.databases.admins import Admin
from sqlalchemy import select
import os


async def handle_admin_add_confirm(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("admin_add_confirm:"):
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
	
	# Handle different confirmation options
	if data == "admin_add_confirm:no":
		# Cancel - return to admin management
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "admin_panel"
				await session.commit()
		
		# Edit the message to show cancellation
		from src.context.messages.replies.admin_add_success import get_cancelled_message
		cancelled_message = get_cancelled_message()
		try:
			await callback.message.edit_text(cancelled_message, reply_markup=None)
		except Exception:
			await callback.message.answer(cancelled_message)
		
		await callback.answer(cancelled_message)
		return
	
	if data.startswith("admin_add_confirm:yes:"):
		# Extract target user ID from callback data
		target_user_id = int(data.split(":")[2])
		
		# Process confirmation (no step validation needed since we reset step in processing message)
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			
			# Find the target user
			target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
			if not target_user:
				await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
				return
			
			# Check if user is already admin
			existing_admin = await session.scalar(select(Admin.id).where(Admin.user_id == target_user.id))
			if existing_admin:
				await callback.answer("❌ این کاربر قبلاً ادمین است.", show_alert=True)
				return
			
			# Add user as admin
			new_admin = Admin(user_id=target_user.id)
			session.add(new_admin)
			await session.commit()
		
		# Send notification to the new admin
		from src.context.messages.notifications.admin_promotion import get_message as get_notification_message
		try:
			await callback.bot.send_message(
				chat_id=target_user.user_id,
				text=get_notification_message(),
				parse_mode="Markdown"
			)
		except Exception as e:
			print(f"LOG: Failed to send admin notification to {target_user.user_id}: {e}")
		
		# Reset step and show success
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "admin_panel"
				await session.commit()
		
		from src.services.admin_list_service import get_admins_list
		from src.context.messages.replies.admin_management_welcome import get_message as get_admin_message
		from src.context.keyboards.inline.admin_management_menu import build_keyboard as build_admin_kb
		
		# Delete the previous message and send a new one
		try:
			await callback.message.delete()
		except Exception:
			pass
		
		admins_list = await get_admins_list()
		user_name = target_user.tg_name or 'نام نامشخص'
		from src.context.messages.replies.admin_add_success import get_success_message
		success_message = get_success_message(user_name)
		await callback.message.answer(success_message, parse_mode="Markdown")
		await callback.message.answer(get_admin_message(admins_list), reply_markup=build_admin_kb(), parse_mode="Markdown")
		from src.context.messages.replies.admin_add_success import get_success_alert
		await callback.answer(get_success_alert())
		return
	
	await callback.answer()
