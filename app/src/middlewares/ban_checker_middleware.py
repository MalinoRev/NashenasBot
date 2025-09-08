from typing import Any, Callable, Dict
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_bans import UserBan
from src.databases.reports import Report
from src.databases.report_categories import ReportCategory
from sqlalchemy import select


class BanCheckerMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Only check for messages and callback queries
		if not isinstance(event, (Message, CallbackQuery)):
			return await handler(event, data)

		# Get user ID
		user_id = None
		if isinstance(event, Message):
			user_id = event.from_user.id if event.from_user else None
		elif isinstance(event, CallbackQuery):
			user_id = event.from_user.id if event.from_user else None

		if not user_id:
			return await handler(event, data)

		# Check if user is banned
		async with get_session() as session:
			# Get user from database
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user:
				return await handler(event, data)

			# Check for active ban
			ban_record: UserBan | None = await session.scalar(
				select(UserBan).where(UserBan.user_id == user.id)
			)

			if ban_record:
				# Check if ban is still active
				is_banned = False
				ban_message = ""

				if ban_record.expiry is None:
					# Permanent ban
					is_banned = True
					ban_message = "🚫 شما به صورت دائمی مسدود شده‌اید."
				elif ban_record.expiry > datetime.utcnow():
					# Temporary ban still active
					is_banned = True
					expiry_date = ban_record.expiry.strftime("%Y-%m-%d %H:%M")
					ban_message = f"🚫 شما مسدود شده‌اید.\n\n📅 تاریخ پایان مسدودیت: {expiry_date}"
				else:
					# Ban has expired, remove it
					await session.delete(ban_record)
					await session.commit()

				# If banned, get report details for the ban message
				if is_banned:
					# Get the most recent approved report that led to this ban
					report: Report | None = await session.scalar(
						select(Report)
						.where(Report.target_id == user.id)
						.where(Report.approved_at.isnot(None))
						.order_by(Report.approved_at.desc())
						.limit(1)
					)
					
					if report:
						# Get category name
						category_name = "سایر موارد"
						if report.category_id:
							category_obj = await session.scalar(
								select(ReportCategory).where(ReportCategory.id == report.category_id)
							)
							if category_obj:
								category_name = category_obj.subject
						
						# Build detailed ban message
						expiry_text = "همیشگی" if ban_record.expiry is None else ban_record.expiry.strftime("%Y-%m-%d %H:%M")
						
						ban_message = (
							f"🚫 <b>شما مسدود شده‌اید</b>\n\n"
							f"📂 <b>دسته‌بندی گزارش:</b> {category_name}\n"
							f"📝 <b>دلیل مسدودیت:</b> {report.reason}\n"
							f"📅 <b>تاریخ رفع مسدودیت:</b> {expiry_text}"
						)

				if is_banned:
					# Send ban message and stop processing
					if isinstance(event, Message):
						await event.answer(ban_message, parse_mode="HTML")
					elif isinstance(event, CallbackQuery):
						await event.answer(ban_message, show_alert=True, parse_mode="HTML")
					return

		# User is not banned, continue with normal processing
		return await handler(event, data)
