from sqlalchemy import select

from src.core.database import get_session
from src.databases.report_categories import ReportCategory


async def seed_report_categories_defaults() -> None:
	"""Seed default rows for report_categories if missing (idempotent by subject)."""
	defaults = [
		"تبلیغات سایت ها و ربات ها و کانال ها",
		"ارسال محتوای غیر اخلاقی",
		"ایجاد مزاحمت",
		"پخش شماره موبایل یا اطلاعات شخصی دیگران",
		"کلمات یا عکس غیر اخلاقی و یا توهین آمیز در پروفایل",
		"جنسیت اشتباه در پروفایل",
	]

	async with get_session() as session:
		result = await session.scalars(select(ReportCategory.subject))
		existing_subjects = set(result.all())

		to_insert: list[ReportCategory] = []
		for subject in defaults:
			if subject not in existing_subjects:
				to_insert.append(ReportCategory(subject=subject))

		if to_insert:
			session.add_all(to_insert)
			await session.commit()



