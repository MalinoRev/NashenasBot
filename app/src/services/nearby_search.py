import math
from datetime import datetime
from typing import Literal

from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.user_locations import UserLocation
from src.databases.likes import Like


GenderFilter = Literal["boys", "girls", "all"]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	# Calculate great-circle distance between two points in kilometers
	r = 6371.0
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1)
	dlam = math.radians(lon2 - lon1)
	a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return r * c


async def generate_nearby_list(tg_user_id: int, max_km: int, gender: GenderFilter) -> tuple[str, bool]:
	"""
	Return (text, ok). If ok is False, text contains an error notice.
	"""
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == tg_user_id))
		if not me:
			return ("حساب کاربری پیدا نشد.", False)
		my_loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == me.id))
		if not my_loc:
			return ("⚠️ ابتدا موقعیت مکانی خود را ثبت کنید.", False)

		# Load candidates with location
		result = await session.execute(
			select(User, UserProfile, UserLocation)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.join(UserLocation, UserLocation.user_id == User.id)
			.where(User.id != me.id)
		)
		rows: list[tuple[User, UserProfile | None, UserLocation]] = [tuple(row) for row in result.all()]

		# Filter by gender
		def gender_ok(profile: UserProfile | None) -> bool:
			if gender == "all":
				return True
			if profile is None or profile.is_female is None:
				return False
			return (not profile.is_female) if gender == "boys" else profile.is_female

		# Compute distances and filter
		filtered: list[tuple[User, UserProfile | None, float]] = []
		for u, p, l in rows:
			if not gender_ok(p):
				continue
			d = _haversine_km(my_loc.location_x, my_loc.location_y, l.location_x, l.location_y)
			if d <= float(max_km):
				filtered.append((u, p, d))

		# Sort by last_activity desc and limit 10
		filtered.sort(key=lambda t: t[0].last_activity, reverse=True)
		filtered = filtered[:10]

		# Fetch likes count per user in one query
		if filtered:
			user_ids = [u.id for u, _, _ in filtered]
			likes_result = await session.execute(
				select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(user_ids)).group_by(Like.target_id)
			)
			likes_counts = dict(likes_result.all())
		else:
			likes_counts = {}

		lines: list[str] = ["📍 لیست افراد نزدیک شما بر اساس آنلاین بودن:", ""]
		for u, p, dist_km in filtered:
			# Prefer profile name; fallback to tg_name; else a placeholder
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
			lines.append(f"🔸 کاربر {name} | {emoji} {gender_word} | سن: {age} | {likes} ❤️")
			lines.append(f"🏁 فاصله: {int(round(dist_km))}KM")
			lines.append(f"👤 پروفایل: /user_{unique_id}")
			lines.append("〰️" * 11)

		if len(lines) <= 2:
			lines.append("نتیجه‌ای مطابق فیلتر پیدا نشد.")

		lines.append("")
		lines.append(f"جستجو شده در {datetime.now().strftime('%Y-%m-%d %H:%M')}")
		return ("\n".join(lines), True)



