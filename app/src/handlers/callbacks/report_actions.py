from aiogram.types import CallbackQuery
from sqlalchemy import select, update
from datetime import datetime

from src.core.database import get_session
from src.databases.reports import Report
from src.databases.users import User


async def handle_report_actions(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("report_"):
		await callback.answer()
		return

	# Extract report ID from callback data
	parts = data.split(":")
	if len(parts) < 2:
		await callback.answer("❌ خطا در پردازش درخواست.", show_alert=True)
		return

	try:
		report_id = int(parts[1])
	except ValueError:
		await callback.answer("❌ شناسه گزارش نامعتبر است.", show_alert=True)
		return

	# Check if user is admin or supporter
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		# Check if user is super admin
		import os
		super_admin_id = os.getenv("TELEGRAM_ADMIN_USER_ID")
		is_super_admin = super_admin_id and str(user_id) == str(super_admin_id)
		
		# Check if user is admin
		from src.databases.admins import Admin
		is_admin = False
		if not is_super_admin:
			admin_exists = await session.scalar(select(Admin.id).where(Admin.user_id == user_id))
			is_admin = bool(admin_exists)
		
		# Check if user is supporter
		from src.databases.supporters import Supporter
		is_supporter = False
		if not is_super_admin and not is_admin:
			supporter_exists = await session.scalar(select(Supporter.id).where(Supporter.user_id == user_id))
			is_supporter = bool(supporter_exists)
		
		if not (is_super_admin or is_admin or is_supporter):
			await callback.answer("❌ شما مجاز به انجام این عمل نیستید.", show_alert=True)
			return

		# Get the report
		report: Report | None = await session.scalar(select(Report).where(Report.id == report_id))
		if not report:
			await callback.answer("❌ گزارش یافت نشد.", show_alert=True)
			return

		# Handle different actions
		if data.startswith("report_reject:"):
			# Update rejected_at timestamp
			await session.execute(
				update(Report)
				.where(Report.id == report_id)
				.values(rejected_at=datetime.utcnow())
			)
			await session.commit()
			
			await callback.answer("✅ گزارش رد شد.", show_alert=True)
			
			# Update the message to show it was rejected
			try:
				await callback.message.edit_text(
					callback.message.text + "\n\n❌ <b>وضعیت: رد شده</b>",
					parse_mode="HTML"
				)
			except Exception as e:
				print(f"LOG: Failed to edit message: {e}")
				pass
			
		elif data.startswith("report_approve:"):
			# Update approved_at timestamp
			await session.execute(
				update(Report)
				.where(Report.id == report_id)
				.values(approved_at=datetime.utcnow())
			)
			await session.commit()
			
			await callback.answer("✅ گزارش تایید شد.", show_alert=True)
			
			# Update the message to show it was approved
			try:
				await callback.message.edit_text(
					callback.message.text + "\n\n✅ <b>وضعیت: تایید شده</b>",
					parse_mode="HTML"
				)
			except Exception as e:
				print(f"LOG: Failed to edit message: {e}")
				pass
			
		elif data.startswith("report_approve_punish:"):
			# Update approved_at timestamp
			await session.execute(
				update(Report)
				.where(Report.id == report_id)
				.values(approved_at=datetime.utcnow())
			)
			await session.commit()
			
			await callback.answer("✅ گزارش تایید شد و کاربر مجازات خواهد شد.", show_alert=True)
			
			# Update the message to show it was approved with punishment
			try:
				await callback.message.edit_text(
					callback.message.text + "\n\n✅ <b>وضعیت: تایید شده و مجازات</b>",
					parse_mode="HTML"
				)
			except Exception as e:
				print(f"LOG: Failed to edit message: {e}")
				pass
			
		elif data.startswith("report_view_user:"):
			# Get target user info
			target_user: User | None = await session.scalar(select(User).where(User.id == report.target_id))
			if not target_user:
				await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
				return
			
			# Show user profile link
			profile_text = (
				f"👤 *اطلاعات کاربر گزارش شده:*\n\n"
				f"🆔 *آیدی کاربر:* {target_user.user_id}\n"
				f"📛 *نام کاربری:* {target_user.tg_name or 'نامشخص'}\n"
				f"🔗 *پروفایل:* /user_{target_user.unique_id}\n\n"
				f"برای مشاهده پروفایل کامل، دستور بالا را ارسال کنید."
			)
			
			await callback.answer(profile_text, show_alert=True)
		
		else:
			await callback.answer("❌ عمل نامشخص است.", show_alert=True)
