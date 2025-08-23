from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.no_command.blocked import get_message as get_blocked_message


# Allowed commands per step (whitelist). Any other command will be blocked.
# Example configuration: allow none by default for sensitive steps.
ALLOWED_COMMANDS_BY_STEP: dict[str, set[str]] = {
	# While searching or sending location, require using on-screen buttons
	"searching": {"/on", "/off", "/credit", "/link", "/instagram"},
	"chatting": set(),
	"sending_location": set(),
}


class NoCommandMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Require authenticated user
		if not data.get("auth_ok", False):
			return await handler(event, data)

		# Only messages can carry slash-commands
		if not isinstance(event, Message):
			return await handler(event, data)

		text = (event.text or "").strip()
		if not text.startswith("/"):
			return await handler(event, data)

		telegram_user_id: Optional[int] = event.from_user.id if event.from_user else None
		if telegram_user_id is None:
			return await handler(event, data)

		# Extract base command token (strip arguments and bot mentions)
		first_token = text.split()[0].lower()
		command_name = first_token.split("@", 1)[0]  # '/start@MyBot' -> '/start'

		async with get_session() as session:
			user_step: Optional[str] = await session.scalar(
				select(User.step).where(User.user_id == telegram_user_id)
			)

		if user_step:
			allowed_set = ALLOWED_COMMANDS_BY_STEP.get(user_step)
			if allowed_set is not None:
				allowed_lower = {cmd.lower() for cmd in allowed_set}
				if command_name not in allowed_lower:
					# Command not allowed in this step
					await event.answer(get_blocked_message())
					return None

		return await handler(event, data)


