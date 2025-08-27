from aiogram.types import CallbackQuery, LinkPreviewOptions
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.direct.confirm_preview import format_message as confirm_text
from src.context.keyboards.inline.direct_send_confirm import build_keyboard as build_confirm_kb
from src.context.messages.commands.start import get_message as get_start_message
from src.context.keyboards.reply.mainButtons import build_keyboard_for
from src.services.direct_draft_cache import get_draft, clear_draft


async def handle_direct_send_confirm(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("direct_send_confirm:"):
		await callback.answer()
		return
	uid = data.split(":", 1)[1]
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not me:
			await callback.answer()
			return
		# Expect step direct_to_{internalId} and a cached draft
		draft = get_draft(me.id)
		if not (getattr(me, "step", "").startswith("direct_to_") and draft is not None):
			await callback.answer()
			return
		from_chat_id, message_id, target_internal_id = draft
		# Fetch target telegram user
		from src.databases.users import User as _U
		target: _U | None = await session.scalar(select(_U).where(_U.id == target_internal_id))
		if not target or not target.user_id:
			await callback.answer("کاربر مقصد یافت نشد.")
			return
		# Charge credit and send
		if int(me.credit or 0) <= 0:
			await callback.answer("❌ موجودی سکه شما کافی نیست.", show_alert=True)
			return
		# Send header with sender link
		from src.context.messages.direct.received_header import format_message as _fmt_header
		# Resolve sender unique id
		sender_uid = me.unique_id if me.unique_id else str(me.id)
		try:
			await callback.message.bot.send_message(chat_id=int(target.user_id), text=_fmt_header(sender_uid))
			# Copy exact original message (supports text/media)
			await callback.message.bot.copy_message(chat_id=int(target.user_id), from_chat_id=from_chat_id, message_id=message_id)
		except Exception:
			pass
		# Deduct and reset
		me.credit = int(me.credit or 0) - 1
		me.step = "start"
		# Clear draft
		clear_draft(me.id)
		await session.commit()
		# Acknowledge and send /start
		name_display = callback.from_user.first_name if callback.from_user else None
		start_text = get_start_message(name_display)
		kb, _ = await build_keyboard_for(user_id)
		try:
			await callback.message.edit_text("✅ پیام شما ارسال شد.")
		except Exception:
			await callback.message.answer("✅ پیام شما ارسال شد.")
		await callback.message.answer(
			start_text,
			reply_markup=kb,
			parse_mode="Markdown",
			link_preview_options=LinkPreviewOptions(is_disabled=True),
		)
		await callback.answer()


async def handle_direct_send_cancel(callback: CallbackQuery) -> None:
	# Cancel and send start
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not me:
			await callback.answer()
			return
		me.step = "start"
		clear_draft(me.id)
		await session.commit()
	try:
		await callback.message.edit_text("🚫 فرآیند ارسال لغو شد.")
	except Exception:
		await callback.message.answer("🚫 فرآیند ارسال لغو شد.")
	name_display = callback.from_user.first_name if callback.from_user else None
	start_text = get_start_message(name_display)
	kb, _ = await build_keyboard_for(user_id)
	await callback.message.answer(
		start_text,
		reply_markup=kb,
		parse_mode="Markdown",
		link_preview_options=LinkPreviewOptions(is_disabled=True),
	)
	await callback.answer()


async def handle_direct_send_edit(callback: CallbackQuery) -> None:
	# Ask user to resend message; keep step as direct_to_{id}
	user_id = callback.from_user.id if callback.from_user else 0
	try:
		await callback.message.edit_text("✏️ لطفاً پیام خود را دوباره ارسال کنید.")
	except Exception:
		await callback.message.answer("✏️ لطفاً پیام خود را دوباره ارسال کنید.")
	await callback.answer()



