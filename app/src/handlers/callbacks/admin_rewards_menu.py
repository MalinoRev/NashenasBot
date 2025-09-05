from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from src.databases.admins import Admin
from sqlalchemy import select
import os


async def handle_admin_rewards_menu(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("admin_rewards:"):
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
	
	# Handle different reward menu options
	if data == "admin_rewards:profile_completion":
		# Set user step to profile reward setting
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "admin_rewards_profile"
				await session.commit()
		
		# Get current reward amount and send prompt message
		from src.context.messages.replies.admin_rewards_profile_prompt import get_message as get_prompt_message
		from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
		from src.databases.rewards import Reward
		
		# Fetch current reward amount
		current_amount = 0
		async with get_session() as session:
			reward: Reward | None = await session.scalar(select(Reward))
			if reward:
				current_amount = reward.profile_amount or 0
		
		# Delete the previous message and send a new one
		try:
			await callback.message.delete()
		except Exception:
			pass
		
		await callback.message.answer(get_prompt_message(current_amount), reply_markup=build_back_kb(), parse_mode="Markdown")
		await callback.answer()
		return
	
	if data == "admin_rewards:referral":
		await callback.answer("👥 تنظیم پاداش معرفی دوستان - در حال توسعه...", show_alert=True)
		return
	
	
	await callback.answer()
