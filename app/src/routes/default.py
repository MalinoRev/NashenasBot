from aiogram import Router
from aiogram.types import Message
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User


router = Router(name="default")


@router.message()
async def handle_default(message: Message) -> None:
	# Intercept direct_list step so default text doesn't respond
	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if user and getattr(user, "step", "").startswith("direct_list_"):
			return
	await message.answer("Default handler: no specific reply found.")


