from aiogram.types import CallbackQuery, LinkPreviewOptions
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.direct_prompt import get_message as get_direct_prompt
from src.context.keyboards.reply.special_contact import build_back_keyboard as build_back_kb
from src.context.keyboards.reply.mainButtons import build_keyboard_for
from src.context.messages.commands.start import get_message as get_start_message
from src.context.alerts.insufficient_credit import get_message as get_insufficient_credit_alert
from src.databases.directs import Direct
from src.services.direct_service import DirectService


def _parse_kind_page(data: str) -> tuple[str | None, int | None]:
	# data formats: direct_list_send_confirm:{kind}:{page}
	try:
		parts = data.split(":", 2)
		if len(parts) < 3:
			return None, None
		rest = parts[2]
		# We built as f"...:{kind}:{page}" so split once from right
		kind, page_str = rest.rsplit(":", 1) if ":" in rest else (rest, "1")
		return kind, int(page_str)
	except Exception:
		return None, None


def _extract_recipients_from_step(step: str) -> list[int]:
	try:
		prefixes = ("direct_list_to_", "direct_list_confirm_to_")
		ids_str = None
		for p in prefixes:
			if step.startswith(p):
				ids_str = step[len(p):]
				break
		if ids_str is None:
			return []
		return [int(x) for x in ids_str.split("-") if x.isdigit()]
	except Exception:
		return []


async def handle_direct_list_send_confirm(callback: CallbackQuery) -> None:
	data = callback.data or ""
	kind, page = _parse_kind_page(data)
	user_id = callback.from_user.id if callback.from_user else 0

	# First: charge coins and reset step
	sender_internal_id: int | None = None
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer()
			return
		recipients = _extract_recipients_from_step(getattr(user, "step", ""))
		cost = len(recipients) if recipients else 0
		balance = int(user.credit or 0)
		# Insufficient balance: alert and keep step unchanged
		if cost > 0 and balance < cost:
			await callback.answer(get_insufficient_credit_alert(), show_alert=True)
			return
		# Deduct and reset step
		if cost > 0:
			user.credit = balance - cost
		user.step = "start"
		sender_internal_id = user.id
		await session.commit()

	# Second: send notification to each recipient for the latest saved direct
	if sender_internal_id:
		service = DirectService(callback.message.bot)
		async with get_session() as session2:
			for rid in _extract_recipients_from_step(getattr(user, "step", "")) if False else recipients:  # reuse computed recipients
				# Resolve recipient telegram id
				target: User | None = await session2.scalar(select(User).where(User.id == rid))
				if not target or not target.user_id:
					continue
				# Fetch latest direct id for (sender_internal_id -> rid)
				direct_obj: Direct | None = await session2.scalar(
					select(Direct).where(Direct.user_id == sender_internal_id, Direct.target_id == rid).order_by(Direct.id.desc())
				)
				if not direct_obj:
					continue
				try:
					await service.send_notification_to_receiver(int(target.user_id), int(direct_obj.id))
				except Exception:
					pass

	# Acknowledge and send /start
	msg = "✅ پیام شما برای ارسال به لیست ثبت شد."
	if 'cost' in locals() and cost > 0:
		msg = f"✅ پیام شما ثبت شد و {cost} سکه کسر گردید."
	try:
		await callback.message.edit_text(msg)
	except Exception:
		await callback.message.answer(msg)

	kb, _ = await build_keyboard_for(user_id)
	await callback.message.answer(
		get_start_message(callback.from_user.first_name if callback.from_user else None),
		reply_markup=kb,
		parse_mode="Markdown",
		link_preview_options=LinkPreviewOptions(is_disabled=True),
	)
	await callback.answer()


async def handle_direct_list_send_cancel(callback: CallbackQuery) -> None:
	data = callback.data or ""
	kind, page = _parse_kind_page(data)
	user_id = callback.from_user.id if callback.from_user else 0

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer()
			return
		user.step = "start"
		await session.commit()

	try:
		await callback.message.edit_text("❌ ارسال پیام به لیست لغو شد.")
	except Exception:
		await callback.message.answer("❌ ارسال پیام به لیست لغو شد.")

	kb, _ = await build_keyboard_for(user_id)
	await callback.message.answer(
		get_start_message(callback.from_user.first_name if callback.from_user else None),
		reply_markup=kb,
		parse_mode="Markdown",
		link_preview_options=LinkPreviewOptions(is_disabled=True),
	)
	await callback.answer()


async def handle_direct_list_send_edit(callback: CallbackQuery) -> None:
	data = callback.data or ""
	kind, page = _parse_kind_page(data)
	if kind is None or page is None:
		await callback.answer()
		return
	user_id = callback.from_user.id if callback.from_user else 0

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user:
			await callback.answer()
			return
		# Set back to collecting message (keep recipients in step)
		# If already in direct_list_to_ / direct_list_confirm_to_, keep it; else fallback to list kind/page
		current_step = getattr(user, "step", "")
		if not (current_step.startswith("direct_list_to_") or current_step.startswith("direct_list_confirm_to_")):
			user.step = f"direct_list_{kind}_{page}"
		await session.commit()

	try:
		await callback.message.delete()
	except Exception:
		pass

	kb_back, _ = build_back_kb()
	await callback.message.answer(get_direct_prompt(), reply_markup=kb_back)
	await callback.answer()


