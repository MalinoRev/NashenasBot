from datetime import datetime
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User


async def get_last_activity_timestamp(user_id_internal: int) -> int | None:
	"""
	Return UNIX timestamp (seconds) of user's last_activity, or None if not found/empty.
	"""
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.id == user_id_internal))
		if not user or not getattr(user, "last_activity", None):
			return None
		dt: datetime = user.last_activity  # type: ignore[assignment]
		return int(dt.timestamp())


