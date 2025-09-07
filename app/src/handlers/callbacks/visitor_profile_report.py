from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.report_categories import ReportCategory
from src.context.messages.replies.profile_report_prompt import get_message as get_prompt_message
from src.context.keyboards.inline.profile_report_categories import build_keyboard as build_categories_kb


async def handle_visitor_profile_report(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("profile_report:"):
		await callback.answer()
		return

	unique_id = data.split(":", 1)[1].strip()
	if not unique_id:
		await callback.answer("شناسه نامعتبر است.", show_alert=True)
		return

	async with get_session() as session:
		# Ensure target user exists (optional validation)
		target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
		if not target:
			await callback.answer("کاربر مورد نظر یافت نشد.", show_alert=True)
			return

		categories = list(await session.scalars(select(ReportCategory).order_by(ReportCategory.id)))

	text = get_prompt_message(unique_id)
	kb = build_categories_kb(unique_id, categories)

	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
	await callback.answer()


