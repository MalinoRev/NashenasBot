from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User


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
		if sender:
			# Reset step
			sender.step = "start"
			await session.commit()
			try:
				from src.context.keyboards.reply.mainButtons import build_keyboard_for
				from src.context.messages.commands.start import get_message as get_start_message
				from aiogram.types import LinkPreviewOptions
				await callback.bot.send_message(int(sender.user_id), f"❌ درخواست شما توسط /user_{sender_unique_id} رد شد")
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


