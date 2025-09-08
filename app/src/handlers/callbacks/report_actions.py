from aiogram.types import CallbackQuery
from sqlalchemy import select, update
from datetime import datetime

from src.core.database import get_session
from src.databases.reports import Report
from src.databases.users import User
from src.databases.admins import Admin


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

		# Check if report has already been processed (admin_id is not null)
		if report.admin_id is not None:
			await callback.answer("❌ قبلاً به این گزارش رسیدگی شده است.", show_alert=True)
			return

		# Handle different actions
		if data.startswith("report_reject:"):
			# Get admin ID for the current user
			admin_id = None
			if is_admin:
				admin_record = await session.scalar(select(Admin).where(Admin.user_id == user_id))
				admin_id = admin_record.id if admin_record else None
			# For super admin and supporters, admin_id remains None
			
			# Update rejected_at timestamp and admin_id
			await session.execute(
				update(Report)
				.where(Report.id == report_id)
				.values(rejected_at=datetime.utcnow(), admin_id=admin_id)
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
			# Get admin ID for the current user
			admin_id = None
			if is_admin:
				admin_record = await session.scalar(select(Admin).where(Admin.user_id == user_id))
				admin_id = admin_record.id if admin_record else None
			# For super admin and supporters, admin_id remains None
			
			# Get report amount from rewards table
			from src.databases.rewards import Reward
			reward_record = await session.scalar(select(Reward))
			report_amount = reward_record.report_amount if reward_record else 0
			
			# Add coins to reporter's credit
			reporter_user = await session.scalar(select(User).where(User.id == report.user_id))
			if reporter_user:
				reporter_user.credit += report_amount
				await session.commit()
				
				# Send confirmation message to reporter
				try:
					from aiogram import Bot
					import os
					bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
					await bot.send_message(
						chat_id=reporter_user.user_id,
						text=f"✅ گزارش شما تایید شد!\n\n💰 {report_amount} سکه به حساب شما اضافه شد.",
						parse_mode="HTML"
					)
				except Exception as e:
					print(f"LOG: Failed to send confirmation to reporter: {e}")
			
			# Update approved_at timestamp and admin_id
			await session.execute(
				update(Report)
				.where(Report.id == report_id)
				.values(approved_at=datetime.utcnow(), admin_id=admin_id)
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
			# Get admin ID for the current user
			admin_id = None
			if is_admin:
				admin_record = await session.scalar(select(Admin).where(Admin.user_id == user_id))
				admin_id = admin_record.id if admin_record else None
			# For super admin and supporters, admin_id remains None
			
			# Get report amount from rewards table
			from src.databases.rewards import Reward
			reward_record = await session.scalar(select(Reward))
			report_amount = reward_record.report_amount if reward_record else 0
			
			# Add coins to reporter's credit
			reporter_user = await session.scalar(select(User).where(User.id == report.user_id))
			if reporter_user:
				reporter_user.credit += report_amount
				await session.commit()
				
				# Send confirmation message to reporter
				try:
					from aiogram import Bot
					import os
					bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
					await bot.send_message(
						chat_id=reporter_user.user_id,
						text=f"✅ گزارش شما تایید شد!\n\n💰 {report_amount} سکه به حساب شما اضافه شد.",
						parse_mode="HTML"
					)
				except Exception as e:
					print(f"LOG: Failed to send confirmation to reporter: {e}")
			
			# Update approved_at timestamp and admin_id
			await session.execute(
				update(Report)
				.where(Report.id == report_id)
				.values(approved_at=datetime.utcnow(), admin_id=admin_id)
			)
			await session.commit()
			
			# Get target user info for punishment prompt
			target_user = await session.scalar(select(User).where(User.id == report.target_id))
			if target_user:
				# Set admin step for punishment input
				admin_user = await session.scalar(select(User).where(User.user_id == user_id))
				if admin_user:
					admin_user.step = f"punish_user:{report.target_id}"
					await session.commit()
					
					# Send punishment prompt message
					punishment_text = (
						f"✅ گزارش تایید شد و کاربر مجازات خواهد شد.\n\n"
						f"👤 <b>کاربر مورد نظر:</b>\n"
						f"🆔 آیدی: {target_user.user_id}\n"
						f"📛 نام کاربری: {target_user.tg_name or 'نامشخص'}\n"
						f"🔗 پروفایل: /user_{target_user.unique_id}\n\n"
						f"⏰ تعداد روزهای مسدودیت را وارد کنید (0-365):\n"
						f"💡 نکته: 0 = مسدودیت همیشگی"
					)
					
					# Create reply keyboard with cancel button
					from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
					kb = ReplyKeyboardMarkup(
						keyboard=[[KeyboardButton(text="لغو مجازات 🔙")]],
						resize_keyboard=True,
						one_time_keyboard=True
					)
					
					try:
						await callback.message.delete()
						await callback.message.answer(punishment_text, reply_markup=kb, parse_mode="HTML")
					except Exception as e:
						print(f"LOG: Failed to send punishment prompt: {e}")
			
			await callback.answer("✅ گزارش تایید شد. حالا تعداد روزهای مسدودیت را وارد کنید.", show_alert=True)
			
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
