from src.core.database import get_session
from src.databases.supporters import Supporter
from src.databases.users import User
from sqlalchemy import select


async def get_supporters_list() -> str:
	"""
	Get formatted list of all supporters for display.
	Returns a friendly message if none found.
	"""
	async with get_session() as session:
		supporters = await session.execute(
			select(Supporter, User)
			.join(User, Supporter.user_id == User.id)
			.order_by(Supporter.id.desc())
		)
		items: list[str] = []
		for supporter, user in supporters:
			info = (
				f"👤 **{user.tg_name or 'نام نامشخص'}**\n"
				f"🆔 **آیدی**: `{user.user_id}`\n"
				f"🆔 **شناسه داخلی**: `{supporter.id}`\n"
				f"📊 **وضعیت**: {'فعال' if getattr(user, 'is_active', True) else 'غیرفعال'}\n"
				"━━━━━━━━━━━━━"
			)
			items.append(info)
		if not items:
			return "❌ هیچ پشتیبانی یافت نشد."
		return "\n\n".join(items)


