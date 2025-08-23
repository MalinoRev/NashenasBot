from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from datetime import datetime

from src.core.database import get_session
from src.databases.users import User


class ActivityMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Require auth to be OK to avoid creating phantom users
		if not data.get("auth_ok", False):
			return await handler(event, data)

		telegram_user_id: Optional[int] = None
		if isinstance(event, Message):
			telegram_user_id = event.from_user.id if event.from_user else None
		elif isinstance(event, CallbackQuery):
			telegram_user_id = event.from_user.id if event.from_user else None
		if not telegram_user_id:
			return await handler(event, data)

		# Update last_activity for this user
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == telegram_user_id))
			if user is not None:
				user.last_activity = datetime.utcnow()
				try:
					await session.commit()
				except Exception:
					pass

		return await handler(event, data)


