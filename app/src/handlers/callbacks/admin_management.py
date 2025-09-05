from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from src.databases.admins import Admin
from sqlalchemy import select
import os


async def handle_admin_management(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("admin_management:"):
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
		if not user or user.step != "admin_panel":
			await callback.answer("❌ شما در پنل مدیریت نیستید.", show_alert=True)
			return
	
	# Handle different admin management options
	if data == "admin_management:add":
		await callback.answer("➕ اضافه کردن ادمین - در حال توسعه...", show_alert=True)
		return
	
	if data == "admin_management:remove":
		await callback.answer("➖ حذف ادمین - در حال توسعه...", show_alert=True)
		return
	
	await callback.answer()
