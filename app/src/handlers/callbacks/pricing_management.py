from aiogram.types import CallbackQuery
from sqlalchemy import select, update
from src.core.database import get_session
from src.databases.users import User
from src.databases.products import Product
from src.context.messages.replies.pricing_set_prompt import get_message as get_prompt_message
from src.context.keyboards.reply.pricing_back import build_keyboard as build_pricing_back_kb


async def handle_pricing_management(callback: CallbackQuery) -> None:
	"""Handle pricing management menu callbacks."""
	# Check if user is admin
	user_id = callback.from_user.id if callback.from_user else 0
	if not user_id:
		await callback.answer("❌ کاربر یافت نشد.")
		return
	
	# Check admin access
	from src.core.database import get_session
	from src.databases.admins import Admin
	import os
	
	is_admin = False
	try:
		admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
		if user_id and admin_env and str(user_id) == str(admin_env):
			is_admin = True
		else:
			async with get_session() as session:
				user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
				if user is not None:
					exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
					is_admin = bool(exists)
	except Exception:
		is_admin = False
	
	if not is_admin:
		await callback.answer("❌ شما دسترسی به این بخش ندارید.")
		return
	
	# Check user step
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_panel":
			await callback.answer("❌ شما در پنل مدیریت نیستید.")
			return
	
	# Get current product values
	async with get_session() as session:
		product: Product | None = await session.scalar(select(Product))
		if not product:
			await callback.answer("❌ اطلاعات تعرفه‌ها یافت نشد.")
			return
	
	# Handle different pricing fields
	callback_data = callback.data or ""
	
	if callback_data == "pricing:vip_price":
		# Set VIP price
		user.step = "pricing_set_vip_price"
		await session.commit()
		
		text = get_prompt_message("تعرفه رنک VIP", int(product.vip_rank_price), "price")
		kb = build_pricing_back_kb()
		
		await callback.message.delete()
		await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
		
	elif callback_data == "pricing:vip_time":
		# Set VIP time
		user.step = "pricing_set_vip_time"
		await session.commit()
		
		text = get_prompt_message("زمان رنک VIP", int(product.vip_rank_time), "time")
		kb = build_pricing_back_kb()
		
		await callback.message.delete()
		await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
		
	elif callback_data == "pricing:delete_price":
		# Set delete price
		user.step = "pricing_set_delete_price"
		await session.commit()
		
		text = get_prompt_message("تعرفه حذف اکانت", int(product.delete_account_price), "price")
		kb = build_pricing_back_kb()
		
		await callback.message.delete()
		await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
		
	elif callback_data == "pricing:unban_price":
		# Set unban price
		user.step = "pricing_set_unban_price"
		await session.commit()
		
		text = get_prompt_message("تعرفه رفع مسدودیت", int(product.unban_price), "price")
		kb = build_pricing_back_kb()
		
		await callback.message.delete()
		await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
	
	await callback.answer()
