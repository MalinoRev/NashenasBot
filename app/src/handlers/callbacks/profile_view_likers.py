from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like


async def handle_profile_view_likers(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not me or getattr(me, "step", "start") != "start":
			await callback.answer("این عملیات فقط در منوی اصلی قابل اجراست.")
			return
		# Delete current message for a clean UI
		try:
			await callback.message.delete()
		except Exception:
			pass
		# Total likes count
		total_count = await session.scalar(select(func.count(Like.id)).where(Like.target_id == me.id))
		total_count = int(total_count or 0)
		# Recent 10 likers with user and profile
		result = await session.execute(
			select(User, UserProfile, Like.created_at)
			.join(Like, Like.user_id == User.id)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.where(Like.target_id == me.id)
			.order_by(Like.created_at.desc())
			.limit(10)
		)
		rows = result.all()
		likers: list[tuple[User, UserProfile | None]] = [(u, p) for (u, p, _) in rows]
		# Likes received per liker (to show their likes count)
		if likers:
			liker_ids = [u.id for u, _ in likers]
			likes_per_user = dict(
				(await session.execute(
					select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(liker_ids)).group_by(Like.target_id)
				)).all()
			)
		else:
			likes_per_user = {}
		# Build text similar to nearby list
		lines: list[str] = ["❤️ لایک‌کننده‌های اخیر شما:", ""]
		for u, p in likers:
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
		if not likers:
			lines.append("فعلاً کسی شما را لایک نکرده است.")
		else:
			remaining = total_count - len(likers)
			if remaining > 0:
				lines.append("")
				lines.append(f"و {remaining} کاربر دیگر …")
		await callback.message.answer("\n".join(lines))
		await callback.answer()



