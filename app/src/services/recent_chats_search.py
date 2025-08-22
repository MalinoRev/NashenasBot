from datetime import datetime
from typing import Literal
import html

from sqlalchemy import select, func, or_

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.chats import Chat
from src.databases.likes import Like


GenderFilter = Literal["boys", "girls", "all"]


async def generate_recent_chats_list(tg_user_id: int, gender: GenderFilter, page: int = 1, page_size: int = 10) -> tuple[str, bool, bool, bool]:
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == tg_user_id))
		if not me:
			return ("حساب کاربری پیدا نشد.", False, False, False)

		# Find recent chats involving me (either side) ordered by created_at desc
		chat_rows = await session.execute(
			select(Chat)
			.where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id))
			.order_by(Chat.created_at.desc())
		)
		chats = [row[0] for row in chat_rows.fetchall()]
		partner_ids: list[int] = []
		for c in chats:
			pid = c.user2_id if c.user1_id == me.id else c.user1_id
			if pid and pid not in partner_ids:
				partner_ids.append(pid)
			if len(partner_ids) >= 50:
				break

		if not partner_ids:
			return ("نتیجه‌ای مطابق فیلتر پیدا نشد.", True, False, False)

		result = await session.execute(
			select(User, UserProfile)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.where(User.id.in_(partner_ids))
		)
		rows: list[tuple[User, UserProfile | None]] = [tuple(row) for row in result.all()]

		def gender_ok(profile: UserProfile | None) -> bool:
			if gender == "all":
				return True
			if profile is None or profile.is_female is None:
				return False
			return (not profile.is_female) if gender == "boys" else profile.is_female

		filtered = [(u, p) for u, p in rows if gender_ok(p)]
		# Keep original recent ordering by chat created_at; partner_ids carry recent order
		order_map = {pid: idx for idx, pid in enumerate(partner_ids)}
		filtered.sort(key=lambda t: order_map.get(t[0].id, 10**9))
		offset = max(0, (int(page) - 1) * int(page_size))
		page_slice = filtered[offset:offset + int(page_size)]
		has_next = len(filtered) > offset + len(page_slice)
		page_has_items = len(page_slice) > 0

		if page_slice:
			user_ids = [u.id for u, _ in page_slice]
			likes_result = await session.execute(
				select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(user_ids)).group_by(Like.target_id)
			)
			likes_counts = dict(likes_result.all())
		else:
			likes_counts = {}

		lines: list[str] = ["🕘 لیست چت‌های اخیر شما:", ""]
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
			block_inner = (
				f"🔸 کاربر {html.escape(str(name))} | {emoji} {gender_word} | سن: {html.escape(str(age))} | {html.escape(str(likes))} ❤️\n"
				f"👤 پروفایل: /user_{html.escape(str(unique_id))}"
			)
			lines.append(f"<blockquote>{block_inner}</blockquote>")

		if len(lines) <= 2:
			lines.append("نتیجه‌ای مطابق فیلتر پیدا نشد.")

		lines.append("")
		lines.append(f"جستجو شده در {datetime.now().strftime('%Y-%m-%d %H:%M')}")
		return ("\n".join(lines), True, has_next, page_has_items)


