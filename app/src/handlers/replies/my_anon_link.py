from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.context.messages.replies.myAnonLink import get_message as get_message1
from src.context.messages.replies.myAnonLink2 import get_message as get_message2


async def handle_my_anon_link(telegram_user_id: int) -> dict:
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == telegram_user_id))
		unique_id = user.unique_id if user else None
		display_name = None
		if user:
			profile: UserProfile | None = await session.scalar(
				select(UserProfile).where(UserProfile.user_id == user.id)
			)
			display_name = profile.name if profile and profile.name else None
		
		message1 = get_message1(unique_id, display_name)
		message2 = get_message2()
		
		return {
			"text": message1,
			"text2": message2
		}


