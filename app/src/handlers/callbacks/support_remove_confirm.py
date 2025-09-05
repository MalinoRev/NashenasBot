from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from src.databases.supporters import Supporter
from sqlalchemy import select
import os


async def handle_support_remove_confirm(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("support_remove_confirm:"):
		await callback.answer()
		return

	user_id = callback.from_user.id if callback.from_user else 0
	# Super admin only
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

	if data == "support_remove_confirm:no":
		# Cancel
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "admin_panel"
				await session.commit()
		from src.context.messages.replies.support_remove_success import get_cancelled_message
		msg = get_cancelled_message()
		try:
			await callback.message.edit_text(msg, reply_markup=None)
		except Exception:
			await callback.message.answer(msg)
		await callback.answer(msg)
		return

	if data.startswith("support_remove_confirm:yes:"):
		target_user_id = int(data.split(":")[2])
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
			if not target_user:
				await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
				return
			# Find supporter row
			supporter = await session.scalar(select(Supporter).where(Supporter.user_id == target_user.id))
			if not supporter:
				await callback.answer("❌ این کاربر پشتیبان نیست.", show_alert=True)
				return
			await session.delete(supporter)
			await session.commit()
		# Reset step
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user:
				user.step = "admin_panel"
				await session.commit()
		# Notify removed supporter
		from src.context.messages.notifications.supporter_removal import get_message as get_removal_message
		from src.context.keyboards.reply.mainButtons import build_keyboard_for
		try:
			kb, _ = await build_keyboard_for(target_user_id)
			await callback.bot.send_message(
				chat_id=target_user.user_id,
				text=get_removal_message(),
				reply_markup=kb,
				parse_mode="Markdown"
			)
		except Exception as e:
			print(f"LOG: Failed to send supporter removal notification to {target_user.user_id}: {e}")
		from src.services.supporter_list_service import get_supporters_list
		from src.context.messages.replies.support_management_welcome import get_message as get_support_message
		from src.context.keyboards.inline.support_management_menu import build_keyboard as build_support_kb
		from src.context.messages.replies.support_remove_success import get_success_message, get_success_alert
		try:
			await callback.message.delete()
		except Exception:
			pass
		user_name = target_user.tg_name or 'نام نامشخص'
		await callback.message.answer(get_success_message(user_name), parse_mode="Markdown")
		supporters_list = await get_supporters_list()
		await callback.message.answer(get_support_message(supporters_list), reply_markup=build_support_kb(), parse_mode="Markdown")
		await callback.answer(get_success_alert())
		return

	await callback.answer()


