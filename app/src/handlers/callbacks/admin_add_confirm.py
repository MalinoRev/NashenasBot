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
	
	# Check user step
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_add":
			await callback.answer("❌ شما در مرحله اضافه کردن ادمین نیستید.", show_alert=True)
			return
	
	# Handle different confirmation options
	if data == "admin_add_confirm:no":
		# Cancel - return to admin management
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
		await callback.message.answer(get_admin_message(admins_list), reply_markup=build_admin_kb(), parse_mode="Markdown")
		await callback.answer("❌ عملیات لغو شد.")
		return
	
	if data.startswith("admin_add_confirm:yes:"):
		# Extract target user ID from callback data
		target_user_id = int(data.split(":")[2])
		
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
		
		# Reset step and show success
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
		user_name = f"{target_user.first_name or 'نام نامشخص'}{' ' + target_user.last_name if target_user.last_name else ''}"
		await callback.message.answer(f"✅ کاربر {user_name} با موفقیت به عنوان ادمین اضافه شد.", parse_mode="Markdown")
		await callback.message.answer(get_admin_message(admins_list), reply_markup=build_admin_kb(), parse_mode="Markdown")
		await callback.answer("✅ ادمین با موفقیت اضافه شد!")
		return
	
	await callback.answer()
