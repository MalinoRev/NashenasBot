from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from src.databases.admins import Admin
from sqlalchemy import select
import os


async def handle_admin_remove_confirm(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("admin_remove_confirm:"):
		await callback.answer()
		return
	
	user_id = callback.from_user.id if callback.from_user else 0
	# Check if user is super admin (only super admins can manage admins)
	is_super_admin = False
	try:
		admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
		if user_id and admin_env and str(user_id) == str(admin_env):
			is_super_admin = True
	except Exception:
		is_super_admin = False
	
	if not is_super_admin:
		await callback.answer("❌ فقط سوپر ادمین‌ها می‌توانند ادمین‌ها را مدیریت کنند.", show_alert=True)
		return
	
	# Handle different confirmation options
	if data == "admin_remove_confirm:no":
		# Cancel - return to admin management
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "admin_panel"
				await session.commit()
		
		# Edit the message to show cancellation
		from src.context.messages.replies.admin_remove_success import get_cancelled_message
		cancelled_message = get_cancelled_message()
		try:
			await callback.message.edit_text(cancelled_message, reply_markup=None)
		except Exception:
			await callback.message.answer(cancelled_message)
		
		await callback.answer(cancelled_message)
		return
	
	if data.startswith("admin_remove_confirm:yes:"):
		# Extract target user ID from callback data
		target_user_id = int(data.split(":")[2])
		
		# Process confirmation
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			
			# Find the target user
			target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
			if not target_user:
				await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
				return
			
			# Check if user is admin
			existing_admin = await session.scalar(select(Admin).where(Admin.user_id == target_user.id))
			if not existing_admin:
				await callback.answer("❌ این کاربر ادمین نیست.", show_alert=True)
				return
			
			# Remove user from admins
			await session.delete(existing_admin)
			
			# Reset removed admin's step to start
			target_user.step = "start"
			await session.commit()
		
		# Send notification to the removed admin
		from src.context.messages.notifications.admin_removal import get_message as get_removal_message
		from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb
		try:
			kb, _ = build_main_kb()
			await callback.bot.send_message(
				chat_id=target_user.user_id,
				text=get_removal_message(),
				reply_markup=kb,
				parse_mode="Markdown"
			)
		except Exception as e:
			print(f"LOG: Failed to send admin removal notification to {target_user.user_id}: {e}")
		
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
		from src.context.messages.replies.admin_remove_success import get_success_message
		success_message = get_success_message(user_name)
		await callback.message.answer(success_message, parse_mode="Markdown")
		await callback.message.answer(get_admin_message(admins_list), reply_markup=build_admin_kb(), parse_mode="Markdown")
		from src.context.messages.replies.admin_remove_success import get_success_alert
		await callback.answer(get_success_alert())
		return
	
	await callback.answer()
