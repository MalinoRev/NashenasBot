from aiogram.types import Message
from sqlalchemy import select, or_

from src.core.database import get_session
from src.databases.users import User
from src.databases.chats import Chat
from src.context.messages.chat.end_confirm import get_message as get_end_confirm
from src.context.keyboards.inline.chat_end_confirm import build_keyboard as build_confirm_kb
from src.context.keyboards.reply.chat_actions import resolve_id_from_text


async def handle_chat_action(message: Message) -> None:
	text = message.text or ""
	action = resolve_id_from_text(text)
	if action != "chat:end":
		return
	user_tg_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
		if not me:
			return
		chat: Chat | None = await session.scalar(
			select(Chat).where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id)).order_by(Chat.id.desc())
		)
		if not chat:
			return
	await message.answer(get_end_confirm(), reply_markup=build_confirm_kb(chat.id))


