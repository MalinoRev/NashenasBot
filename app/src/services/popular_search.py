from datetime import datetime
from typing import Literal
import html

from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like
from src.services.user_activity import get_last_activity_string


GenderFilter = Literal["boys", "girls", "all"]


async def generate_popular_list(tg_user_id: int, gender: GenderFilter, page: int = 1, page_size: int = 10) -> tuple[str, bool, bool, bool]:
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == tg_user_id))
		if not me:
			return ("حساب کاربری پیدا نشد.", False, False, False)

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

		def profile_complete(profile: UserProfile | None) -> bool:
			return (
				profile is not None
				and profile.name is not None
				and profile.is_female is not None
				and profile.age is not None
				and profile.state is not None
				and profile.city is not None
			)

		def gender_ok(profile: UserProfile | None) -> bool:
			if gender == "all":
				return True
			if profile is None or profile.is_female is None:
				return False
			return (not profile.is_female) if gender == "boys" else profile.is_female

		filtered = [(u, p) for u, p in rows if profile_complete(p) and gender_ok(p)]
		# Sort by like count desc then last_activity desc
		filtered.sort(key=lambda t: (-(likes_counts.get(t[0].id, 0)), t[0].last_activity), reverse=False)
		offset = max(0, (int(page) - 1) * int(page_size))
		page_slice = filtered[offset:offset + int(page_size)]
		has_next = len(filtered) > offset + len(page_slice)
		page_has_items = len(page_slice) > 0

		lines: list[str] = ["⭐ لیست کاربران محبوب بر اساس تعداد لایک:", ""]
		for u, p in page_slice:
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
			status = await get_last_activity_string(u.id)
			block_inner = (
				f"🔸 {html.escape(str(likes))} ❤️ | {html.escape(str(name))} | {emoji} {gender_word} | سن: {html.escape(str(age))}\n"
				f"👤 پروفایل: /user_{html.escape(str(unique_id))}\n"
				f"آخرین فعالیت: {html.escape(status or 'نامشخص')}"
			)
			lines.append(f"<blockquote>{block_inner}</blockquote>")
			lines.append("〰️" * 11)

		if len(lines) <= 2:
			lines.append("نتیجه‌ای مطابق فیلتر پیدا نشد.")

		lines.append("")
		lines.append(f"جستجو شده در {datetime.now().strftime('%Y-%m-%d %H:%M')}")
		return ("\n".join(lines), True, has_next, page_has_items)


