from aiogram.types import CallbackQuery, LinkPreviewOptions
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.direct.confirm_preview import format_message as confirm_text
from src.context.keyboards.inline.direct_send_confirm import build_keyboard as build_confirm_kb
from src.context.messages.commands.start import get_message as get_start_message
from src.context.keyboards.reply.mainButtons import build_keyboard_for
from src.services.direct_draft_cache import get_draft, clear_draft
from src.services.direct_service import DirectService
from src.services.cache import CacheService


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
		from_chat_id, message_id, target_internal_id, message_data = draft
		# Fetch target telegram user
		from src.databases.users import User as _U
		target: _U | None = await session.scalar(select(_U).where(_U.id == target_internal_id))
		if not target or not target.user_id:
			await callback.answer("کاربر مقصد یافت نشد.")
			return
		# Charge credit
		if int(me.credit or 0) <= 0:
			await callback.answer("❌ موجودی سکه شما کافی نیست.", show_alert=True)
			return

		# Initialize services
		direct_service = DirectService(callback.message.bot)
		cache_service = CacheService(callback.message.bot)

		# Process the stored message data
		json_message_data = {}

		if message_data.text:
			json_message_data = {
				"message": message_data.text[:200],  # Limit to 200 chars
				"type": "text"
			}
		elif message_data.photo:
			# Save photo to cache
			media_id = await cache_service.save_media(message_data.photo[-1])
			json_message_data = {
				"message": message_data.caption or "",  # Store caption, empty string if no caption
				"type": "image",
				"media_id": media_id  # Can be None if CACHE_CHANNEL_ID not set
			}
		elif message_data.video:
			# Save video to cache
			media_id = await cache_service.save_media(message_data.video)
			json_message_data = {
				"message": message_data.caption or "",  # Store caption, empty string if no caption
				"type": "video",
				"media_id": media_id  # Can be None if CACHE_CHANNEL_ID not set
			}
		elif message_data.animation:
			# Save animation to cache
			media_id = await cache_service.save_media(message_data.animation)
			json_message_data = {
				"message": message_data.caption or "",  # Store caption, empty string if no caption
				"type": "animation",
				"media_id": media_id  # Can be None if CACHE_CHANNEL_ID not set
			}
		elif message_data.audio:
			# Save audio to cache
			media_id = await cache_service.save_media(message_data.audio)
			json_message_data = {
				"message": message_data.caption or "",  # Store caption, empty string if no caption
				"type": "audio",
				"media_id": media_id  # Can be None if CACHE_CHANNEL_ID not set
			}
		elif message_data.document:
			# Save document to cache
			media_id = await cache_service.save_media(message_data.document)
			json_message_data = {
				"message": message_data.caption or "",  # Store caption, empty string if no caption
				"type": "document",
				"media_id": media_id  # Can be None if CACHE_CHANNEL_ID not set
			}
		elif message_data.sticker:
			# Save sticker to cache
			media_id = await cache_service.save_media(message_data.sticker)
			json_message_data = {
				"message": "",
				"type": "sticker",
				"media_id": media_id  # Can be None if CACHE_CHANNEL_ID not set
			}
		else:
			await callback.answer("❌ نوع پیام پشتیبانی نمی‌شود", show_alert=True)
			return

		# Save direct message to database
		direct_id = await direct_service.save_direct(me.id, target.id, json_message_data)
		if not direct_id:
			await callback.answer("❌ خطا در ذخیره‌سازی پیام", show_alert=True)
			return

		# Deduct credit and reset step
		me.credit = int(me.credit or 0) - 1
		me.step = "start"
		clear_draft(me.id)
		await session.commit()

		# Send notification to receiver
		await direct_service.send_notification_to_receiver(int(target.user_id), direct_id)

		# Acknowledge and send /start
		name_display = callback.from_user.first_name if callback.from_user else None
		start_text = get_start_message(name_display)
		kb, _ = await build_keyboard_for(user_id)
		try:
			await callback.message.edit_text("✅ پیام شما با موفقیت ذخیره شد و برای دریافت‌کننده ارسال خواهد شد.")
		except Exception:
			await callback.message.answer("✅ پیام شما با موفقیت ذخیره شد و برای دریافت‌کننده ارسال خواهد شد.")
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



