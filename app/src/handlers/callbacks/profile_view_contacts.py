from aiogram.types import CallbackQuery
from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.contacts import Contact
from src.databases.likes import Like


def _format_user_line(u: User, p: UserProfile | None, likes_count: int) -> list[str]:
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
	return [
		f"🔸 کاربر {name} | {emoji} {gender_word} | سن: {age} | {likes_count} ❤️",
		f"👤 پروفایل: /user_{unique_id}",
		"〰️" * 11,
	]


async def handle_profile_view_contacts(callback: CallbackQuery) -> None:
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
		# Fetch all contacts (targets that this user has contacted)
		result = await session.execute(
			select(User, UserProfile)
			.join(Contact, Contact.target_id == User.id)
			.join(UserProfile, UserProfile.user_id == User.id, isouter=True)
			.where(Contact.user_id == me.id)
			.order_by(Contact.created_at.desc())
		)
		rows = result.all()
		contacts: list[tuple[User, UserProfile | None]] = [(u, p) for (u, p) in rows]
		if not contacts:
			await callback.message.answer("لیست مخاطبین شما خالی است.")
			await callback.answer()
			return
		# Likes per contact
		contact_ids = [u.id for u, _ in contacts]
		likes_per_user = dict(
			(await session.execute(
				select(Like.target_id, func.count(Like.id)).where(Like.target_id.in_(contact_ids)).group_by(Like.target_id)
			)).all()
		)
		# Chunk into pages of 10 users and send multiple messages
		page_size = 10
		for i in range(0, len(contacts), page_size):
			chunk = contacts[i : i + page_size]
			lines: list[str] = ["👥 لیست مخاطبین شما:", ""]
			for u, p in chunk:
				likes_count = likes_per_user.get(u.id, 0)
				lines.extend(_format_user_line(u, p, likes_count))
			await callback.message.answer("\n".join(lines))
		await callback.answer()



