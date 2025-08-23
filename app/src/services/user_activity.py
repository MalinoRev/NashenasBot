from datetime import datetime, timedelta
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


async def get_last_activity_string(user_id_internal: int) -> str:
	"""
	Return a human-friendly Persian string for last activity:
	- "در حال چت" if step == chatting
	- "لحظاتی پیش" for < 1 minute
	- "N دقیقه پیش" for < 60 minutes
	- "N ساعت پیش" for < 24 hours
	- "N روز پیش" otherwise
	- "نامشخص" if no last activity record
	"""
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.id == user_id_internal))
		if not user:
			return "نامشخص"
		# If currently chatting, override
		if getattr(user, "step", None) == "chatting":
			return "در حال چت"
		last: datetime | None = getattr(user, "last_activity", None)
		if not last:
			return "نامشخص"
		delta: timedelta = datetime.utcnow() - last
		seconds = int(delta.total_seconds())
		if seconds < 60:
			return "لحظاتی پیش"
		minutes = seconds // 60
		if minutes < 60:
			return f"{minutes} دقیقه پیش"
		hours = minutes // 60
		if hours < 24:
			return f"{hours} ساعت پیش"
		days = hours // 24
		return f"{days} روز پیش"


