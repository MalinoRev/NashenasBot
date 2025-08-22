import math
from datetime import datetime
from typing import Literal
import html

from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.user_locations import UserLocation
from src.databases.likes import Like


GenderFilter = Literal["boys", "girls", "all"]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	r = 6371.0
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1)
	dlam = math.radians(lon2 - lon1)
	a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return r * c


async def generate_location_list(tg_user_id: int, latitude: float, longitude: float, max_km: int, gender: GenderFilter, page: int = 1, page_size: int = 10) -> tuple[str, bool, bool, bool]:
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == tg_user_id))
		if not me:
			return ("حساب کاربری پیدا نشد.", False, False, False)

		result = await session.execute(
			select(User, UserProfile, UserLocation)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.join(UserLocation, UserLocation.user_id == User.id, isouter=True)
			.where(User.id != me.id)
		)
		rows: list[tuple[User, UserProfile | None, UserLocation | None]] = [tuple(row) for row in result.all()]

		def gender_ok(profile: UserProfile | None) -> bool:
			if gender == "all":
				return True
			if profile is None or profile.is_female is None:
				return False
			return (not profile.is_female) if gender == "boys" else profile.is_female

		filtered: list[tuple[User, UserProfile | None, float]] = []
		for u, p, l in rows:
			if not gender_ok(p):
				continue
			if l is None or l.location_x is None or l.location_y is None:
				continue
			d = _haversine_km(latitude, longitude, l.location_x, l.location_y)
			if d <= float(max_km):
				filtered.append((u, p, d))

		filtered.sort(key=lambda t: t[0].last_activity, reverse=True)
		offset = max(0, (int(page) - 1) * int(page_size))
		page_slice = filtered[offset:offset + int(page_size)]
		has_next = len(filtered) > offset + len(page_slice)
		page_has_items = len(page_slice) > 0

		if page_slice:
			user_ids = [u.id for u, _, _ in page_slice]
			likes_result = await session.execute(
				select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(user_ids)).group_by(Like.target_id)
			)
			likes_counts = dict(likes_result.all())
		else:
			likes_counts = {}

		lines: list[str] = ["📍 لیست نزدیک‌ترین افراد به موقعیت ارسال‌شده:", ""]
		for u, p, dist_km in page_slice:
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
			block_inner = (
				f"🔸 کاربر {html.escape(str(name))} | {emoji} {gender_word} | سن: {html.escape(str(age))} | {html.escape(str(likes))} ❤️\n"
				f"🏁 فاصله: {int(round(dist_km))}KM\n"
				f"👤 پروفایل: /user_{html.escape(str(unique_id))}"
			)
			lines.append(f"<blockquote>{block_inner}</blockquote>")

		if len(lines) <= 2:
			lines.append("نتیجه‌ای مطابق فیلتر پیدا نشد.")

		lines.append("")
		lines.append(f"جستجو شده در {datetime.now().strftime('%Y-%m-%d %H:%M')}")
		return ("\n".join(lines), True, has_next, page_has_items)


