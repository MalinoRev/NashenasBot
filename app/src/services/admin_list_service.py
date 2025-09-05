from src.core.database import get_session
from src.databases.admins import Admin
from src.databases.users import User
from sqlalchemy import select


async def get_admins_list() -> str:
	"""
	Get formatted list of all admins for display
	Returns empty string if no admins found
	"""
	async with get_session() as session:
		# Get all admins with their user information
		admins = await session.scalars(
			select(Admin, User)
			.join(User, Admin.user_id == User.id)
			.order_by(Admin.id.desc())
		)
		
		admin_list = []
		for admin, user in admins:
			# Format admin info similar to search results
			admin_info = (
				f"👤 **{user.tg_name or 'نام نامشخص'}**\n"
				f"🆔 **آیدی**: `{user.user_id}`\n"
				f"🆔 **شناسه داخلی**: `{admin.id}`\n"
				f"📊 **وضعیت**: {'فعال' if getattr(user, 'is_active', True) else 'غیرفعال'}\n"
				"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			)
			admin_list.append(admin_info)
		
		if not admin_list:
			return "❌ هیچ ادمینی یافت نشد."
		
		return "\n\n".join(admin_list)
