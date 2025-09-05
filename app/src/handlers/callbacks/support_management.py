from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select
import os


async def handle_support_management(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("support_management:"):
		await callback.answer()
		return

	user_id = callback.from_user.id if callback.from_user else 0
	# Check if user is super admin (same restriction as admin management)
	is_super_admin = False
	try:
		admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
		if user_id and admin_env and str(user_id) == str(admin_env):
			is_super_admin = True
	except Exception:
		is_super_admin = False

	if not is_super_admin:
		await callback.answer("❌ فقط سوپر ادمین‌ها می‌توانند پشتیبان‌ها را مدیریت کنند.", show_alert=True)
		return

	# Check user step
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_panel":
			await callback.answer("❌ شما در پنل مدیریت نیستید.", show_alert=True)
			return

	# Handle options
	if data == "support_management:add":
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "support_add"
				await session.commit()
		from src.context.messages.replies.support_add_prompt import get_message as get_prompt_message
		from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_prompt_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
		await callback.answer()
		return

	if data == "support_management:remove":
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "support_remove"
				await session.commit()
		from src.context.messages.replies.support_remove_prompt import get_message as get_prompt_message
		from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_prompt_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
		await callback.answer()
		return

	await callback.answer()


