from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.chats import Chat
from src.context.messages.chat.connected import get_message as get_chat_connected
from src.context.keyboards.reply.chat_actions import build_keyboard as build_chat_actions_kb


async def handle_chat_request_reject(callback: CallbackQuery) -> None:
	data = callback.data or ""
	parts = data.split(":", 1)
	if len(parts) < 2:
		await callback.answer()
		return
	sender_unique_id = parts[1]
	# Delete the decision message
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer("❌ درخواست کاربر رد شد.")
	# Notify the requester and reset their step
	async with get_session() as session:
		sender: User | None = await session.scalar(select(User).where(User.unique_id == sender_unique_id))
		rejecter: User | None = await session.scalar(select(User).where(User.user_id == (callback.from_user.id if callback.from_user else 0)))
		if sender:
			# Reset step
			sender.step = "start"
			await session.commit()
			try:
				from src.context.keyboards.reply.mainButtons import build_keyboard_for
				from src.context.messages.commands.start import get_message as get_start_message
				from aiogram.types import LinkPreviewOptions
				rejecter_uid = (rejecter.unique_id if rejecter and rejecter.unique_id else (str(rejecter.id) if rejecter else ""))
				await callback.bot.send_message(int(sender.user_id), f"❌ درخواست شما توسط /user_{rejecter_uid} رد شد")
				name_display = None
				# Cannot access requester's name here; send generic start
				kb, _ = await build_keyboard_for(sender.user_id)
				await callback.bot.send_message(
					int(sender.user_id),
					get_start_message(None),
					reply_markup=kb,
					parse_mode="Markdown",
					link_preview_options=LinkPreviewOptions(is_disabled=True),
				)
			except Exception:
				pass
	await callback.answer()
	return


async def handle_chat_request_accept(callback: CallbackQuery) -> None:
	data = callback.data or ""
	parts = data.split(":", 1)
	if len(parts) < 2:
		await callback.answer()
		return
	sender_unique_id = parts[1]
	# Accept: set both steps to chatting, create chat row, notify both sides with chat UI
	async with get_session() as session:
		sender: User | None = await session.scalar(select(User).where(User.unique_id == sender_unique_id))
		receiver_tg_id = callback.from_user.id if callback.from_user else 0
		receiver: User | None = await session.scalar(select(User).where(User.user_id == receiver_tg_id))
		if not sender or not receiver:
			await callback.answer()
			return
		# Update steps
		sender.step = "chatting"
		receiver.step = "chatting"
		# Create chat row
		chat = Chat(user1_id=sender.id, user2_id=receiver.id)
		session.add(chat)
		await session.commit()
	# Delete decision message
	try:
		await callback.message.delete()
	except Exception:
		pass
	# Send connected message to both
	try:
		kb1, _ = build_chat_actions_kb()
		await callback.bot.send_message(int(sender.user_id), get_chat_connected(), reply_markup=kb1)
	except Exception:
		pass
	try:
		kb2, _ = build_chat_actions_kb()
		await callback.message.answer(get_chat_connected(), reply_markup=kb2)
	except Exception:
		pass
	await callback.answer()
	return


