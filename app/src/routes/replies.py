from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, LinkPreviewOptions
from src.context.keyboards.reply.mainButtons import resolve_id_from_text as resolve_main_id
from src.context.keyboards.reply.random_match import resolve_id_from_text as resolve_random_match_reply_id
from src.context.keyboards.reply.nearby import resolve_id_from_text as resolve_nearby_reply_id
from src.handlers.replies.chat_actions import handle_chat_action
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb, build_keyboard_for
from src.context.messages.commands.start import get_message as get_start_message


router = Router(name="replies")


@router.message()
async def handle_text_reply(message: Message) -> None:
	print(f"LOG: handle_text_reply called with text: '{message.text}'")
	# This router handles plain text messages that are not commands
	if message.text and message.text.startswith("/"):
		print("LOG: Message starts with '/', letting commands router handle it")
		# Let commands router handle it
		return

	text = message.text or ""
	# Intercept chat actions (reply buttons in chat)
	await handle_chat_action(message)

	# Handle edit photo flow: accept only photo
	from src.core.database import get_session
	from src.databases.users import User
	from sqlalchemy import select
	from src.context.messages.profileMiddleware.invalidPhoto import get_message as get_invalid_photo
	from src.context.messages.profileMiddleware.photoSaved import get_message as get_photo_saved
	from pathlib import Path
	from aiogram.types import LinkPreviewOptions

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == (message.from_user.id if message.from_user else 0)))
		if user and user.step == "edit_photo":
			if not message.photo:
				await message.answer(get_invalid_photo())
				return
			# Pick the best quality photo (last size)
			photo_sizes = message.photo
			file_id = photo_sizes[-1].file_id
			# Download to storage path (use aiogram's download helper for reliability in container)
			avatars_dir = Path("src") / "storage" / "avatars"
			avatars_dir.mkdir(parents=True, exist_ok=True)
			file_path = avatars_dir / f"{user.id}.jpg"
			bot = message.bot
			# Use Telegram API to download file by id
			await bot.download(file_id, destination=str(file_path))
			# Reset step
			user.step = "start"
			await session.commit()
			# Send success + /start
			await message.answer(get_photo_saved())
			name = (message.from_user.first_name if message.from_user else None) or (message.from_user.username if message.from_user else None)
			start_text = get_start_message(name)
			kb, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
			await message.answer(start_text, reply_markup=kb, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True))
			return

	# Handle sending location (reply button sends location payload)
	if message.location is not None:
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.user_locations import UserLocation
		from sqlalchemy import select
		from src.context.messages.callbacks.nearby import get_location_saved_success
		from src.context.messages.callbacks.search_by_location_gender import get_message as get_gender_message
		from src.context.keyboards.inline.search_by_location_gender import build_keyboard as build_gender_kb
		from src.services.location_search import generate_location_list

		user_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user:
				return
			if user.step == "sending_location":
				# Original nearby/profile flow: persist location
				loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == user.id))
				if loc is None:
					loc = UserLocation(user_id=user.id, location_x=message.location.latitude, location_y=message.location.longitude)
					session.add(loc)
				else:
					loc.location_x = message.location.latitude
					loc.location_y = message.location.longitude
				user.step = "start"
				await session.commit()
				await message.answer(get_location_saved_success())
				# Also send /start exactly as elsewhere
				name = (message.from_user.first_name if message.from_user else None) or (message.from_user.username if message.from_user else None)
				start_text = get_start_message(name)
				kb, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
				await message.answer(
					start_text,
					reply_markup=kb,
					parse_mode="Markdown",
					link_preview_options=LinkPreviewOptions(is_disabled=True),
				)
				return
			if user.step == "search_sending_location":
				# Temporary flow: do not persist, immediately ask for gender selection with this location cached in memory by encoding coords in callback data
				lat = message.location.latitude
				lon = message.location.longitude
				# Reset step back to start so further messages behave normally
				user.step = "start"
				await session.commit()
				# First, send a tiny message to restore main keyboard
				name = (message.from_user.first_name if message.from_user else None) or (message.from_user.username if message.from_user else None)
				start_text = get_start_message(name)
				kb_main, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
				await message.answer("در حال پردازش...", reply_markup=kb_main)
				# Then show gender keyboard
				await message.answer(get_gender_message(), reply_markup=build_gender_kb())
				# Attach a hint with the coordinates encoded expectation
				# We will handle the next callback with a global variable is not safe; instead, send hidden state via separate mapping isn't present
				# For simplicity here, we will store last temp coords in memory keyed by user_id via a module-level cache
				from src.services.temp_location_cache import set_temp_location
				set_temp_location(user.id, float(lat), float(lon))
				return

	# Handle random_match cancel reply button
	rm_id = resolve_random_match_reply_id(text)
	if rm_id == "random_match:cancel":
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.chat_queue import ChatQueue
		from sqlalchemy import select, delete

		user_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "searching":
				return
			# Delete any queue records for this user (by internal users.id)
			await session.execute(delete(ChatQueue).where(ChatQueue.user_id == user.id))
			# Set step back to start
			user.step = "start"
			await session.commit()
		# Send the same start message + main keyboard as /start
		name = (message.from_user.first_name if message.from_user else None) or (message.from_user.username if message.from_user else None)
		start_text = get_start_message(name)
		kb, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
		await message.answer(
			start_text,
			reply_markup=kb,
			parse_mode="Markdown",
			link_preview_options=LinkPreviewOptions(is_disabled=True),
		)
		return

	# Handle nearby back reply button
	nearby_id = resolve_nearby_reply_id(text)
	from src.context.keyboards.reply.special_contact import resolve_id_from_text as resolve_special_back
	special_id = resolve_special_back(text)
	print(f"LOG: Checking back buttons - nearby_id: '{nearby_id}', special_id: '{special_id}'")
	if nearby_id == "nearby:back" or nearby_id == "search:back" or special_id == "special:back":
		print(f"LOG: Back button detected: nearby='{nearby_id}', special='{special_id}'")
		from src.core.database import get_session
		from src.databases.users import User
		from src.services.chat_request_service import ChatRequestService
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user:
				return

			# Handle chat request cancellation
			if user.step.startswith("chat_request_to_"):
				print(f"LOG: Chat request cancellation detected for step: '{user.step}'")
				# Extract target ID from step
				try:
					target_db_id = int(user.step.replace("chat_request_to_", ""))
					print(f"LOG: Extracted target_db_id = {target_db_id}")

					# Get target user's Telegram ID from database
					print(f"LOG: Looking for target user with id = {target_db_id}")
					target_user: User | None = await session.scalar(select(User).where(User.id == target_db_id))
					if not target_user:
						print(f"LOG: Target user with id {target_db_id} not found")
						await message.answer("❌ کاربر مورد نظر یافت نشد.")
						return

					target_telegram_id = target_user.user_id
					print(f"LOG: Target user found: id={target_user.id}, user_id={target_telegram_id}, unique_id='{target_user.unique_id}'")

					# Cancel the chat request
					print(f"LOG: Calling cancel_chat_request with user.id={user.id}, target_db_id={target_db_id}")
					success, message_id_to_delete = await ChatRequestService.cancel_chat_request(user.id, target_db_id)
					print(f"LOG: cancel_chat_request result: success={success}, message_id_to_delete={message_id_to_delete}")

					if success:
						# Delete the notification message from target user
						if message_id_to_delete:
							try:
								print(f"LOG: Deleting message {message_id_to_delete} from chat {target_telegram_id}")
								await message.bot.delete_message(
									chat_id=int(target_telegram_id),
									message_id=message_id_to_delete
								)
								print("LOG: Message deleted successfully")
							except Exception as e:
								print(f"ERROR: Failed to delete notification message {message_id_to_delete}: {e}")

						await message.answer("✅ درخواست چت کنسل شد.")
						print("LOG: Cancellation completed successfully")
					else:
						await message.answer("❌ خطا در کنسل کردن درخواست.")
						print("LOG: Cancellation failed")

				except (ValueError, Exception) as e:
					print(f"ERROR: Failed to parse target ID from step {user.step}: {e}")
					await message.answer("❌ خطا در کنسل کردن درخواست.")

			# Allow back for several transient steps
			if user.step not in ("sending_location", "search_sending_location", "search_special_contact") and not user.step.startswith("chat_request_to_"):
				return

			user.step = "start"
			await session.commit()

		# Send the same start message + main keyboard as /start
		name = (message.from_user.first_name if message.from_user else None) or (message.from_user.username if message.from_user else None)
		start_text = get_start_message(name)
		kb, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
		await message.answer(
			start_text,
			reply_markup=kb,
			parse_mode="Markdown",
			link_preview_options=LinkPreviewOptions(is_disabled=True),
		)
		return

	# Handle special contact flow input
	from src.core.database import get_session as _get_session_sc
	from src.databases.users import User as _User_sc
	from sqlalchemy import select as _select_sc
	if text or message.forward_from or message.contact:
		user_id_sc = message.from_user.id if message.from_user else 0
		async with _get_session_sc() as session_sc:
			user_sc: _User_sc | None = await session_sc.scalar(_select_sc(_User_sc).where(_User_sc.user_id == user_id_sc))
			if user_sc and user_sc.step == "search_special_contact":
				# Try to resolve target user's internal id by 3 ways
				tg_numeric_id: int | None = None
				# Way 1: forwarded message contains original sender id
				if getattr(message, "forward_from", None) and message.forward_from:
					if getattr(message.forward_from, "id", None):
						tg_numeric_id = int(message.forward_from.id)
				# Way 2: contact payload contains user_id
				if tg_numeric_id is None and getattr(message, "contact", None) and message.contact:
					if getattr(message.contact, "user_id", None):
						tg_numeric_id = int(message.contact.user_id)
				# Way 3: pure numeric text id
				if tg_numeric_id is None and text.isdigit():
					tg_numeric_id = int(text)
				# Lookup in users table by Telegram numeric id
				from sqlalchemy import select as _select2
				from src.databases.users import User as _User2
				target_unique_id: str | None = None
				if tg_numeric_id is not None:
					u2: _User2 | None = await session_sc.scalar(_select2(_User2).where(_User2.user_id == tg_numeric_id))
					if u2:
						target_unique_id = u2.unique_id
				# Reset step to start regardless
				user_sc.step = "start"
				await session_sc.commit()
				# Build main keyboard
				kb_main, _ = build_main_kb()
				if target_unique_id:
					await message.answer(
						f"✅ کاربر عضو ربات است. برای مشاهده پروفایل این دستور را بفرستید:\n/user_{target_unique_id}",
						reply_markup=kb_main,
					)
				else:
					await message.answer(
						"❌ کاربر یافت نشد یا عضو ربات نیست.",
						reply_markup=kb_main,
					)
				return

	main_id = resolve_main_id(text)
	print(f"LOG: main_id resolved from text '{text}': '{main_id}'")
	if main_id == "main:my_anon_link":
		print("LOG: My anon link button clicked")
		from src.handlers.replies.my_anon_link import handle_my_anon_link
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				# User step is not 'start', don't send anything
				return
		
		# User step is 'start', proceed with handler
		result = await handle_my_anon_link(user_id)
		
		# Send first message
		await message.answer(result.get("text", ""))
		
		# Send second message
		if result.get("text2"):
			await message.answer(result.get("text2"))
		return

	if main_id == "main:random_match":
		from src.handlers.replies.random_match import handle_random_match
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_random_match()
		await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"))
		return

	if main_id == "main:nearby":
		from src.handlers.replies.nearby import handle_nearby
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_nearby(user_id)
		await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"))
		return

	if main_id == "main:search":
		from src.handlers.replies.search import handle_search
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_search()
		await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"))
		return

	if main_id == "main:profile":
		from src.handlers.replies.profile import handle_profile
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return
		result = await handle_profile(user_id)
		photo_path = result.get("photo_path")
		caption = result.get("caption")
		kb_inline = result.get("reply_markup")
		if photo_path and caption:
			photo = FSInputFile(photo_path)
			await message.answer_photo(photo, caption=caption, reply_markup=kb_inline)
		return

	if main_id == "main:invite":
		from src.handlers.replies.invite import handle_invite
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_invite(user_id)
		# Send photo with caption first
		photo_path = result.get("photo_path")
		caption = result.get("caption")
		if photo_path and caption:
			photo = FSInputFile(photo_path)
			await message.answer_photo(photo, caption=caption)
		# Then send second text message if any
		if result.get("text"):
			await message.answer(result.get("text"))
		return

	if main_id == "main:help":
		from src.handlers.replies.help import handle_help
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_help()
		await message.answer(result.get("text", ""))
		return

	if main_id == "main:coin":
		from src.handlers.replies.coin import handle_coin
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select

		user_id = message.from_user.id if message.from_user else 0
		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_coin(user_id)
		await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"))
		return

	await message.answer("🔸 متوجه نشدم چی میخوای 🙃\n\nاگر نیاز به کمک داری دستور /help رو بفرست")


