from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.context.messages.callbacks.direct_intro import get_message as get_direct_intro
from src.context.messages.callbacks.direct_prompt import get_message as get_direct_prompt
from src.context.keyboards.inline.direct_confirm import build_keyboard as build_direct_confirm_kb
from src.context.keyboards.reply.special_contact import build_back_keyboard as build_back_kb


async def handle_visitor_profile_direct(callback: CallbackQuery) -> None:
	data = callback.data or ""
	# Extract unique_id
	unique_id = data.split(":", 1)[1] if ":" in data else ""
	async with get_session() as session:
		# Resolve target by unique_id
		target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
		if not target:
			await callback.answer("کاربر یافت نشد.", show_alert=True)
			return
		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == target.id))
		name = (profile.name if profile and profile.name else None) or (target.tg_name or "بدون نام")
		gender_text = "دختر" if (profile and profile.is_female) else ("پسر" if (profile and profile and profile.is_female is False) else "نامشخص")
		age = str(profile.age) if profile and profile.age is not None else "?"

	if data.startswith("profile_direct:"):
		# Show intro with cost and confirm button
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(
			get_direct_intro(name=name, gender_text=gender_text, age=age, unique_id=unique_id),
			reply_markup=build_direct_confirm_kb(unique_id),
		)
		await callback.answer()
		return

	if data.startswith("direct_confirm:"):
		# Set step for the sender to collect the direct message text
		viewer_id = callback.from_user.id if callback.from_user else 0
		async with get_session() as session2:
			viewer: User | None = await session2.scalar(select(User).where(User.user_id == viewer_id))
			if not viewer:
				await callback.answer()
				return
			viewer.step = f"direct_to_{target.id}"
			await session2.commit()
		try:
			await callback.message.delete()
		except Exception:
			pass
		kb_back, _ = build_back_kb()
		await callback.message.answer(get_direct_prompt(), reply_markup=kb_back)
		await callback.answer()
		return


