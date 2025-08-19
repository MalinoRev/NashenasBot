from datetime import datetime
from typing import Literal

from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like


GenderFilter = Literal["boys", "girls", "all"]


async def generate_popular_list(tg_user_id: int, gender: GenderFilter) -> tuple[str, bool]:
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == tg_user_id))
		if not me:
			return ("حساب کاربری پیدا نشد.", False)

		result = await session.execute(
			select(User, UserProfile)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.where(User.id != me.id)
		)
		rows: list[tuple[User, UserProfile | None]] = [tuple(row) for row in result.all()]

		# Prefetch like counts for all users
		if rows:
			user_ids = [u.id for u, _ in rows]
			likes_result = await session.execute(
				select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(user_ids)).group_by(Like.target_id)
			)
			likes_counts = dict(likes_result.all())
		else:
			likes_counts = {}

		def gender_ok(profile: UserProfile | None) -> bool:
			if gender == "all":
				return True
			if profile is None or profile.is_female is None:
				return False
			return (not profile.is_female) if gender == "boys" else profile.is_female

		filtered = [(u, p) for u, p in rows if gender_ok(p)]
		# Sort by like count desc then last_activity desc
		filtered.sort(key=lambda t: (-(likes_counts.get(t[0].id, 0)), t[0].last_activity), reverse=False)
		filtered = filtered[:10]

		lines: list[str] = ["⭐ لیست کاربران محبوب بر اساس تعداد لایک:", ""]
		for u, p in filtered:
			likes = likes_counts.get(u.id, 0)
			name = (p.name if p and p.name else None) or (u.tg_name or "بدون نام")
			age = p.age if p and p.age is not None else "?"
			if p and p.is_female is True:
				emoji = "👩"
				gender_word = "دختر"
			elif p and p.is_female is False:
				emoji = "👨"
				gender_word = "پسر"
			else:
				emoji = "❔"
				gender_word = "نامشخص"
			unique_id = u.unique_id or str(u.id)
			lines.append(f"🔸 {likes} ❤️ | {name} | {emoji} {gender_word} | سن: {age}")
			lines.append(f"👤 پروفایل: /user_{unique_id}")
			lines.append("〰️" * 11)

		if len(lines) <= 2:
			lines.append("نتیجه‌ای مطابق فیلتر پیدا نشد.")

		lines.append("")
		lines.append(f"جستجو شده در {datetime.now().strftime('%Y-%m-%d %H:%M')}")
		return ("\n".join(lines), True)


