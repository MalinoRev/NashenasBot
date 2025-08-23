from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select, or_

from src.core.database import get_session
from src.databases.users import User
from src.databases.chats import Chat
from src.databases.chat_history import ChatHistory
from src.context.keyboards.reply.chat_actions import resolve_id_from_text
from src.handlers.replies.chat_actions import handle_chat_action


class ChatForwardMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message,
		data: Dict[str, Any],
	) -> Any:
		# Only plain messages; skip commands
		if not isinstance(event, Message):
			return await handler(event, data)
		if (event.text or "").startswith("/"):
			return await handler(event, data)
		user_tg_id: Optional[int] = event.from_user.id if event.from_user else None
		if not user_tg_id:
			return await handler(event, data)
		# Intercept chat action buttons so they act locally and do not get forwarded
		action = resolve_id_from_text(event.text or "")
		if action is not None:
			await handle_chat_action(event)
			return None
		async with get_session() as session:
			me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
			if not me or getattr(me, "step", "start") != "chatting":
				return await handler(event, data)
			# Find active chat partner (latest created chat where I'm user1 or user2 and not ended)
			chat: Chat | None = await session.scalar(
				select(Chat)
				.where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id))
				.order_by(Chat.id.desc())
			)
			if not chat:
				return await handler(event, data)
			partner_id = chat.user2_id if chat.user1_id == me.id else chat.user1_id
			partner: User | None = await session.scalar(select(User).where(User.id == partner_id))
			if not partner or not partner.user_id:
				return await handler(event, data)
			# Forward/copy user's message to partner
			try:
				sent = await event.bot.copy_message(chat_id=int(partner.user_id), from_chat_id=event.chat.id, message_id=event.message_id)
				# Persist chat history
				ch = ChatHistory(
					user_id=me.id,
					target_id=partner.id,
					chat_id=chat.id,
					received_message_id=event.message_id,
					sent_message_id=getattr(sent, "message_id", 0),
				)
				async with get_session() as session2:
					session2.add(ch)
					await session2.commit()
			except Exception:
				pass
			return None


