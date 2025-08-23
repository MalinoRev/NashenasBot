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
		# Intercept delete commands on replied messages
		if (event.reply_to_message is not None) and (event.text or "").strip().lower() in {"del", "delete", "حذف"}:
			async with get_session() as session0:
				me0: User | None = await session0.scalar(select(User).where(User.user_id == user_tg_id))
				if not me0:
					return None
				# Find latest chat
				chat0: Chat | None = await session0.scalar(
					select(Chat).where(or_(Chat.user1_id == me0.id, Chat.user2_id == me0.id)).order_by(Chat.id.desc())
				)
				if not chat0:
					return None
				# Lookup chat history by my message id
				replied_id = event.reply_to_message.message_id
				rec: ChatHistory | None = await session0.scalar(
					select(ChatHistory).where(
						ChatHistory.chat_id == chat0.id,
						ChatHistory.received_message_id == replied_id,
					)
				)
				if not rec:
					# Not my message; notify
					from src.context.messages.chat.delete_not_allowed import get_message as get_del_not_allowed
					await event.answer(get_del_not_allowed())
					return None
				# It is my message: delete my message and the bot-sent copy for partner
				try:
					await event.bot.delete_message(chat_id=event.chat.id, message_id=replied_id)
				except Exception:
					pass
				# Delete partner's copy
				partner_id0 = chat0.user2_id if chat0.user1_id == me0.id else chat0.user1_id
				partner0: User | None = await session0.scalar(select(User).where(User.id == partner_id0))
				if partner0 and partner0.user_id:
					try:
						await event.bot.delete_message(chat_id=int(partner0.user_id), message_id=int(rec.sent_message_id))
					except Exception:
						pass
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
				sent = await event.bot.copy_message(
					chat_id=int(partner.user_id),
					from_chat_id=event.chat.id,
					message_id=event.message_id,
					protect_content=bool(chat.secure_chat),
				)
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


