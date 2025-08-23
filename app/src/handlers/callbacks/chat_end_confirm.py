from aiogram.types import CallbackQuery
from sqlalchemy import select, or_

from src.core.database import get_session
from src.databases.users import User
from src.databases.chats import Chat


async def handle_chat_end_no(callback: CallbackQuery) -> None:
	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.answer()
	return


async def handle_chat_end_yes(callback: CallbackQuery) -> None:
	data = callback.data or ""
	parts = data.split(":", 1)
	if len(parts) < 2:
		await callback.answer()
		return
	chat_id = int(parts[1])
	user_tg_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
		if not me:
			await callback.answer()
			return
		chat: Chat | None = await session.scalar(select(Chat).where(Chat.id == chat_id))
		if not chat:
			await callback.answer()
			return
		# Resolve both users
		u1: User | None = await session.scalar(select(User).where(User.id == chat.user1_id))
		u2: User | None = await session.scalar(select(User).where(User.id == chat.user2_id))
		if not u1 or not u2:
			await callback.answer()
			return
		# Set steps back to start
		u1.step = "start"
		u2.step = "start"
		await session.commit()
	# Delete confirm message
	try:
		await callback.message.delete()
	except Exception:
		pass
	# Notify both sides with personalized text
	def _format(u_me: User, u_partner: User) -> str:
		stopper = "شما" if u_me.user_id == user_tg_id else "مخاطب شما"
		partner_uid = u_partner.unique_id or str(u_partner.id)
		return (
			f"چت شما با /user_{partner_uid} توسط {stopper} قطع شد\n\n"
			"برای گزارش عدم رعایت قوانین (/help_terms) می‌توانید با لمس 《 🚫 گزارش کاربر 》 در پروفایل، کاربر را گزارش کنید.\n"
			"🗑تا 30 دقیقه بعد اتمام چت می‌تونی با دستور زیر پیام‌های ارسال شده رو به طرف مقابل پاک کنی!\n"
			f"/delete_messages_{chat_id}"
		)
	try:
		await callback.bot.send_message(int(u1.user_id), _format(u1, u2))
		await callback.bot.send_message(int(u2.user_id), _format(u2, u1))
	except Exception:
		pass
	# Send start to both
	from src.context.keyboards.reply.mainButtons import build_keyboard_for
	from src.context.messages.commands.start import get_message as get_start_message
	from aiogram.types import LinkPreviewOptions
	try:
		kb1, _ = await build_keyboard_for(u1.user_id)
		await callback.bot.send_message(int(u1.user_id), get_start_message(None), reply_markup=kb1, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True))
		kb2, _ = await build_keyboard_for(u2.user_id)
		await callback.bot.send_message(int(u2.user_id), get_start_message(None), reply_markup=kb2, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True))
	except Exception:
		pass
	await callback.answer()
	return


