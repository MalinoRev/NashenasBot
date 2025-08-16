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
		# Should run after auth/profile; if those failed, skip
		if not data.get("auth_ok", False):
			return None
		# Profile middleware may block commands until completion, but we still enforce channels after profile is OK
		# For callbacks, let specific handlers manage flow; enforce only on messages for now
		if isinstance(event, CallbackQuery):
			return await handler(event, data)

		async with get_session() as session:
			channels: List[RequestedChannel] = list(
				await session.scalars(select(RequestedChannel).order_by(RequestedChannel.id))
			)
			if not channels:
				return await handler(event, data)

			# Build inline keyboard via context builder
			markup = build_channel_join_kb([c.channel_id for c in channels])

			# Send prompt and stop further processing
			await event.answer(get_required_message(), reply_markup=markup)
			return None
