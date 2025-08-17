from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_locations import UserLocation
from src.context.messages.replies.nearby import get_location_missing_message, get_choose_distance_message
from src.context.keyboards.inline.nearby import build_request_location_keyboard, build_distance_keyboard


async def handle_nearby(user_id: int) -> dict:
	# Check location presence
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			return {"text": get_location_missing_message(), "reply_markup": build_request_location_keyboard()}
		loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == user.id))
		if loc is None:
			return {"text": get_location_missing_message(), "reply_markup": build_request_location_keyboard()}
		# Location exists → show distance choices
		return {"text": get_choose_distance_message(), "reply_markup": build_distance_keyboard()}



