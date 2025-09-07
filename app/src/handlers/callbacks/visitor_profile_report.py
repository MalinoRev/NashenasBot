from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.report_categories import ReportCategory
from src.context.messages.replies.profile_report_prompt import get_message as get_prompt_message
from src.context.keyboards.inline.profile_report_categories import build_keyboard as build_categories_kb
from src.context.keyboards.reply.special_contact import build_back_keyboard as build_back_kb


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


async def handle_report_category_click(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("report_category:"):
		await callback.answer()
		return

	# data format: report_category:{unique_id}:{category_id|other}
	_, unique_id, category_value = data.split(":", 2)

	# Persist user's step and temp context
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		viewer: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not viewer:
			await callback.answer()
			return
		# Save step including unique_id and chosen category marker
		viewer.step = f"report_write:{unique_id}:{category_value}"
		await session.commit()

	# Build reply back keyboard
	kb, _ = build_back_kb()

	# First warning message
	try:
		await callback.message.answer("تمامی گزارشات بررسی خواهند شد و 🔴 ارسال گزارشات اشتباه موجب مسدود شدن شما خواهد شد.")
	except Exception:
		pass
	# Second instruction message
	second = (
		"⚠️ فرم ارسال گزارش عدم رعایت قوانین به دلیل دیگر موارد...\n\n"
		"خب حالا کافیه یه توضیح دقیق و 《کامل》 درباره گزارشت بفرستی تا ثبتش کنم.\n"
		"- مثلا : داره تبلیغات فلان کانال رو توی چت ( یا پروفایلش ) میکنه.\n\n"
		"برای لغو گزارش 《 🔙 بازگشت 》 را انتخاب کنید 👇"
	)
	await callback.message.answer(second, reply_markup=kb)
	await callback.answer()


