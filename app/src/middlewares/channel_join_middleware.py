from typing import Any, Callable, Dict, Optional, List

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from src.core.database import get_session
from src.databases.requested_channels import RequestedChannel
from src.context.messages.channel_join.required import get_message as get_required_message
from src.context.keyboards.inline.channelJoin import build_keyboard as build_channel_join_kb


class ChannelJoinMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Require auth to be OK first
		if not data.get("auth_ok", False):
			return None

		# Resolve Telegram user id
		user_id: Optional[int] = None
		if isinstance(event, Message):
			user_id = event.from_user.id if event.from_user else None
		elif isinstance(event, CallbackQuery):
			user_id = event.from_user.id if event.from_user else None
		if not user_id:
			return None

		# Load required channels
		async with get_session() as session:
			channels: List[RequestedChannel] = list(
				await session.scalars(select(RequestedChannel).order_by(RequestedChannel.id))
			)
			if not channels:
				return await handler(event, data)

		# Bot instance for membership checks
		bot = data.get("bot")
		if bot is None:
			return await handler(event, data)

		# Verify membership in all channels
		not_joined: List[str] = []
		for ch in channels:
			chat_identifier = f"@{ch.channel_id}" if not str(ch.channel_id).startswith("@") else str(ch.channel_id)
			try:
				member = await bot.get_chat_member(chat_identifier, user_id)
				status = getattr(member, "status", None)
				if status not in {"creator", "administrator", "member"}:
					not_joined.append(str(ch.channel_id))
			except Exception:
				# If check fails, assume not joined
				not_joined.append(str(ch.channel_id))

		if not not_joined:
			return await handler(event, data)

		# Build prompt and keyboard
		markup = build_channel_join_kb([c for c in not_joined])
		text = get_required_message()

		# Send prompt depending on event type
		if isinstance(event, Message):
			await event.answer(text, reply_markup=markup)
		else:
			if event.message:
				await event.message.answer(text, reply_markup=markup)
			else:
				# Fallback: show alert
				await event.answer(text, show_alert=True)
		return None
