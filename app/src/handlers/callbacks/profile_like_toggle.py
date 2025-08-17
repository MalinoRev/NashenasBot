from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like
from src.databases.states import State
from src.databases.cities import City
from src.context.messages.replies.profile import format_profile_caption
from src.context.keyboards.inline.profile import build_profile_keyboard


async def handle_profile_like_toggle(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer("حساب یافت نشد.")
			return
		# Only from main menu
		if getattr(user, "step", "start") != "start":
			await callback.answer("این عملیات فقط در منوی اصلی قابل اجراست.")
			return
		# Toggle like receiving state
		current = bool(getattr(user, "can_get_likes", True))
		user.can_get_likes = not current
		await session.commit()
		# Delete current message
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Rebuild and resend profile
		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
		likes_result = await session.execute(select(Like).where(Like.target_id == user.id))
		likes_count = len(likes_result.all())
		name = (profile.name if profile and profile.name else None) or (user.tg_name or "بدون نام")
		age = str(profile.age) if profile and profile.age is not None else "?"
		gender_text = "دختر" if profile and profile.is_female else ("پسر" if profile and profile and profile.is_female is not None else "نامشخص")
		state_name = "—"
		city_name = "—"
		if profile and profile.state is not None:
			state_name_val = await session.scalar(select(State.state_name).where(State.id == profile.state))
			if state_name_val:
				state_name = state_name_val
		if profile and profile.city is not None:
			city_name_val = await session.scalar(select(City.city_name).where(City.id == profile.city))
			if city_name_val:
				city_name = city_name_val
		unique_id = user.unique_id or str(user.id)
		caption = format_profile_caption(
			name=name,
			gender_text=gender_text,
			state_name=state_name,
			city_name=city_name,
			age=age,
			like_count=likes_count,
			unique_id=unique_id,
		)
		photo_path = "src/context/resources/images/noimage-girl.jpg" if (profile and profile.is_female) else "src/context/resources/images/noimage-boy.jpg"
		kb = build_profile_keyboard(is_like_active=bool(user.can_get_likes))
		photo = FSInputFile(photo_path)
		await callback.message.answer_photo(photo, caption=caption, reply_markup=kb)
		await callback.answer("وضعیت لایک {} شد.".format("فعال" if user.can_get_likes else "غیرفعال"))



