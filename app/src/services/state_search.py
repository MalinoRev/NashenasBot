from datetime import datetime
from typing import Literal
import html

from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like


GenderFilter = Literal["boys", "girls", "all"]


async def generate_state_list(tg_user_id: int, gender: GenderFilter, page: int = 1, page_size: int = 10) -> tuple[str, bool, bool, bool]:
	"""
	Return (text, ok). If ok is False, text contains an error notice.
	Lists up to 10 users from the same state as the requester.
	"""
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == tg_user_id))
		if not me:
			return ("حساب کاربری پیدا نشد.", False, False, False)
		my_profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == me.id))
		if not my_profile or my_profile.state is None:
			return ("⚠️ ابتدا استان خود را در پروفایل تکمیل کنید.", False, False, False)

		# Load candidates with profile and same state
		result = await session.execute(
			select(User, UserProfile)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.where(User.id != me.id)
		)
		rows: list[tuple[User, UserProfile | None]] = [tuple(row) for row in result.all()]

		def gender_ok(profile: UserProfile | None) -> bool:
			if gender == "all":
				return True
			if profile is None or profile.is_female is None:
				return False
			return (not profile.is_female) if gender == "boys" else profile.is_female

		# Filter by same state and gender
		filtered: list[tuple[User, UserProfile | None]] = []
		for u, p in rows:
			if p is None or p.state is None:
				continue
			if p.state != my_profile.state:
				continue
			if not gender_ok(p):
				continue
			filtered.append((u, p))

		# Sort and paginate
		filtered.sort(key=lambda t: t[0].last_activity, reverse=True)
		offset = max(0, (int(page) - 1) * int(page_size))
		page_slice = filtered[offset:offset + int(page_size)]
		page_has_items = len(page_slice) > 0
		has_next = len(filtered) > offset + len(page_slice)

		# Fetch likes count per user in one query
		if page_slice:
			user_ids = [u.id for u, _ in page_slice]
			likes_result = await session.execute(
				select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(user_ids)).group_by(Like.target_id)
			)
			likes_counts = dict(likes_result.all())
		else:
			likes_counts = {}

		lines: list[str] = ["🎌 لیست هم استانی‌های شما بر اساس آنلاین بودن:", ""]
		for u, p in page_slice:
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
			likes = likes_counts.get(u.id, 0)
			unique_id = u.unique_id or str(u.id)
			# Wrap each user block in an HTML blockquote for Telegram quoting
			block_inner = (
				f"🔸 کاربر {html.escape(str(name))} | {emoji} {gender_word} | سن: {html.escape(str(age))} | {html.escape(str(likes))} ❤️\n"
				f"👤 پروفایل: /user_{html.escape(str(unique_id))}"
			)
			lines.append(f"<blockquote>{block_inner}</blockquote>")
			lines.append("〰️" * 11)

		if len(lines) <= 2:
			lines.append("نتیجه‌ای مطابق فیلتر پیدا نشد.")

		lines.append("")
		lines.append(f"جستجو شده در {datetime.now().strftime('%Y-%m-%d %H:%M')}")
		return ("\n".join(lines), True, has_next, page_has_items)


