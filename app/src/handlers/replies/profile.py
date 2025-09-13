from sqlalchemy import select, func
from aiogram.types import FSInputFile
from pathlib import Path

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like
from src.databases.states import State
from src.databases.cities import City
from src.context.messages.replies.profile import format_profile_caption
from src.services.user_activity import get_last_activity_string
from src.context.keyboards.inline.profile import build_profile_keyboard
from src.databases.user_locations import UserLocation
from src.context.messages.replies.profile_completion_reminder import get_message as get_completion_reminder
from src.databases.rewards import Reward


async def handle_profile(user_id: int) -> dict:
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return {"text": "حساب کاربری یافت نشد."}
		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
		likes_count = 0
		likes_row = await session.execute(select(func.count(Like.id)).where(Like.target_id == user.id))
		likes_count = likes_row.scalar_one() or 0
		name = (profile.name if profile and profile.name else None) or (user.tg_name or "بدون نام")
		age = str(profile.age) if profile and profile.age is not None else "?"
		gender_text = "دختر" if profile and profile.is_female else ("پسر" if profile and profile and profile.is_female is not None else "نامشخص")
		# Fetch state/city names if present
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
		status = await get_last_activity_string(user.id)
		caption = format_profile_caption(
			name=name,
			gender_text=gender_text,
			state_name=state_name,
			city_name=city_name,
			age=age,
			like_count=likes_count,
			unique_id=unique_id,
			last_activity=status,
		)
		# Prefer user custom avatar if exists under src/storage/avatars/{user_db_id}.jpg
		# Resolve inside container relative to app root; check multiple known locations
		avatar_dirs = [
			(Path("storage") / "avatars").resolve(),
			(Path("src") / "storage" / "avatars").resolve(),
		]
		photo_path = None
		for avatars_dir in avatar_dirs:
			candidates = [
				avatars_dir / f"{user.id}.jpg",
				avatars_dir / f"{user.id}.jpeg",
				avatars_dir / f"{user.id}.png",
			]
			custom_path = next((p for p in candidates if p.exists()), None)
			if custom_path is None and avatars_dir.exists():
				for p in avatars_dir.glob(f"{user.id}.*"):
					custom_path = p
					break
			if custom_path is not None and custom_path.exists():
				photo_path = str(custom_path.resolve())
				break
		# Fallback to default gender-based images
		if not photo_path:
			photo_path = "src/context/resources/images/noimage-girl.jpg" if (profile and profile.is_female) else "src/context/resources/images/noimage-boy.jpg"
		keyboard = build_profile_keyboard(is_like_active=bool(getattr(user, "can_get_likes", True)))

		# Completion reminder: check for missing photo and location
		missing_steps = 0
		# 1) Photo: consider custom avatar exists if photo_path points to custom file
		custom_photo_exists = False
		try:
			# If resolved path is under storage avatars and not default noimage
			custom_photo_exists = (
				photo_path is not None
				and ("noimage-girl.jpg" not in str(photo_path))
				and ("noimage-boy.jpg" not in str(photo_path))
			)
		except Exception:
			custom_photo_exists = False
		if not custom_photo_exists:
			missing_steps += 1
		# 2) Location: exists if a row present in user_locations
		location_exists = bool(await session.scalar(select(func.count()).select_from(UserLocation).where(UserLocation.user_id == user.id)))
		if not location_exists:
			missing_steps += 1

		reminder_text = None
		if missing_steps > 0:
			# Fetch referral/profile completion reward amount
			reward: Reward | None = await session.scalar(select(Reward))
			reward_amount = int(getattr(reward, "profile_amount", 0)) if reward else 0
			reminder_text = get_completion_reminder(missing_steps, reward_amount)

		return {"photo_path": photo_path, "caption": caption, "reply_markup": keyboard, "reminder_text": reminder_text}



