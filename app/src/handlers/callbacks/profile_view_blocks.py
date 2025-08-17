from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like
from src.databases.user_blocked import UserBlocked


async def handle_profile_view_blocks(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not me or getattr(me, "step", "start") != "start":
			await callback.answer("این عملیات فقط در منوی اصلی قابل اجراست.")
			return
		# Clean previous message
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Total blocks
		total_count = await session.scalar(select(func.count(UserBlocked.id)).where(UserBlocked.user_id == me.id))
		total_count = int(total_count or 0)
		# Recent 10 blocked targets with their user/profile
		result = await session.execute(
			select(User, UserProfile, UserBlocked.created_at)
			.join(UserBlocked, UserBlocked.target_id == User.id)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.where(UserBlocked.user_id == me.id)
			.order_by(UserBlocked.created_at.desc())
			.limit(10)
		)
		rows = result.all()
		blocked: list[tuple[User, UserProfile | None]] = [(u, p) for (u, p, _) in rows]
		# Likes per blocked user (optional, for same output style)
		if blocked:
			user_ids = [u.id for u, _ in blocked]
			likes_per_user = dict(
				(await session.execute(
					select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(user_ids)).group_by(Like.target_id)
				)).all()
			)
		else:
			likes_per_user = {}
		# Build text similar to likers list
		lines: list[str] = ["🚫 لیست کاربرانی که شما بلاک کرده‌اید:", ""]
		for u, p in blocked:
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
			likes_count = likes_per_user.get(u.id, 0)
			unique_id = u.unique_id or str(u.id)
			lines.append(f"🔸 کاربر {name} | {emoji} {gender_word} | سن: {age} | {likes_count} ❤️")
			lines.append(f"👤 پروفایل: /user_{unique_id}")
			lines.append("〰️" * 11)
		if not blocked:
			lines.append("شما هنوز کسی را بلاک نکرده‌اید.")
		else:
			remaining = total_count - len(blocked)
			if remaining > 0:
				lines.append("")
				lines.append(f"و {remaining} کاربر دیگر …")
		await callback.message.answer("\n".join(lines))
		await callback.answer()



