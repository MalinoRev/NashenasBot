from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, LinkPreviewOptions
from src.context.keyboards.reply.mainButtons import resolve_id_from_text as resolve_main_id
from src.context.keyboards.reply.random_match import resolve_id_from_text as resolve_random_match_reply_id
from src.context.keyboards.reply.nearby import resolve_id_from_text as resolve_nearby_reply_id
from src.handlers.replies.chat_actions import handle_chat_action
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb, build_keyboard_for
from src.context.messages.commands.start import get_message as get_start_message
from src.databases.users import User


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
			if user.step in ("sending_location", "search_sending_location", "search_special_contact") or user.step.startswith("chat_request_to_"):
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

	if main_id == "admin:panel":
		from src.handlers.replies.admin_panel import handle_admin_panel
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.admins import Admin
		from sqlalchemy import select
		import os

		user_id = message.from_user.id if message.from_user else 0
		# Check if user is admin
		is_admin = False
		try:
			admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
			if user_id and admin_env and str(user_id) == str(admin_env):
				is_admin = True
			else:
				if user_id:
					async with get_session() as session:
						user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
						if user is not None:
							exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
							is_admin = bool(exists)
		except Exception:
			is_admin = False
		
		if not is_admin:
			await message.answer("❌ شما دسترسی به پنل مدیریت ندارید.")
			return

		# Check user step before calling handler
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "start":
				return

		result = await handle_admin_panel(user_id)
		await message.answer(result.get("text", ""), reply_markup=result.get("reply_markup"), parse_mode="Markdown")
		return

	# Handle admin rewards profile setting step
	from src.core.database import get_session
	from src.databases.users import User
	from src.databases.admins import Admin
	from sqlalchemy import select
	import os
	
	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if user and user.step == "admin_rewards_profile":
			# Check if user is admin
			is_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_admin = True
				else:
					if user_id:
						exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
						is_admin = bool(exists)
			except Exception:
				is_admin = False
			
			if not is_admin:
				await message.answer("❌ شما دسترسی به این بخش ندارید.")
				return
			
			# Handle back button
			from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
			back_id = resolve_back_id(text)
			if back_id == "admin_rewards:back":
				# Return to admin panel
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
				kb, _ = build_admin_kb()
				await message.answer(get_admin_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Validate and process the new amount
			try:
				# Normalize Persian/Arabic digits
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				
				if not normalized_text.isdigit():
					from src.context.messages.replies.admin_rewards_profile_success import get_invalid_amount_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_invalid_amount_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				new_amount = int(normalized_text)
				
				if new_amount < 0 or new_amount > 100000:
					from src.context.messages.replies.admin_rewards_profile_success import get_invalid_amount_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_invalid_amount_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				# Update the reward amount in database
				from src.databases.rewards import Reward
				reward: Reward | None = await session.scalar(select(Reward))
				if not reward:
					reward = Reward(profile_amount=new_amount)
					session.add(reward)
				else:
					reward.profile_amount = new_amount
				
				await session.commit()
				
				# Reset step and show success
				user.step = "admin_panel"
				await session.commit()
				
				from src.context.messages.replies.admin_rewards_profile_success import get_message as get_success_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
				kb, _ = build_admin_kb()
				await message.answer(get_success_message(new_amount), reply_markup=kb, parse_mode="Markdown")
				return
				
			except Exception as e:
				from src.context.messages.replies.admin_rewards_profile_success import get_invalid_amount_message
				from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
				await message.answer(get_invalid_amount_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
				return

		# Handle admin remove step
		if user and user.step == "admin_remove":
			# Check if user is super admin
			is_super_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_super_admin = True
			except Exception:
				is_super_admin = False
			
			if not is_super_admin:
				await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند ادمین‌ها را مدیریت کنند.")
				return
			
			# Handle back button
			from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
			back_id = resolve_back_id(text)
			if back_id == "admin_rewards:back":
				# Return to main admin panel
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Validate and process the user ID
			try:
				# Normalize Persian/Arabic digits
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				
				if not normalized_text.isdigit():
					from src.context.messages.replies.admin_remove_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				target_user_id = int(normalized_text)
				
				# Check if user exists in database
				target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
				if not target_user:
					from src.context.messages.replies.admin_remove_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				# Check if user is admin
				existing_admin = await session.scalar(select(Admin.id).where(Admin.user_id == target_user.id))
				if not existing_admin:
					from src.context.messages.replies.admin_remove_confirm import get_not_admin_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_not_admin_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				# Show processing message first and reset step
				user.step = "admin_panel"
				await session.commit()
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer("⏳ در حال پردازش...", reply_markup=kb)
				
				# Show confirmation
				from src.context.messages.replies.admin_remove_confirm import get_message as get_confirm_message
				from src.context.keyboards.inline.admin_remove_confirm import build_keyboard as build_confirm_kb
				
				user_name = target_user.tg_name or 'نام نامشخص'
				await message.answer(get_confirm_message(user_name, target_user_id), reply_markup=build_confirm_kb(target_user_id), parse_mode="Markdown")
				return
				
			except Exception as e:
				from src.context.messages.replies.admin_remove_confirm import get_user_not_found_message
				from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
				await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
				return

		# Handle admin add step
		if user and user.step == "admin_add":
			# Check if user is super admin
			is_super_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_super_admin = True
			except Exception:
				is_super_admin = False
			
			if not is_super_admin:
				await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند ادمین‌ها را مدیریت کنند.")
				return
			
			# Handle back button
			from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
			back_id = resolve_back_id(text)
			if back_id == "admin_rewards:back":
				# Return to main admin panel
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Validate and process the user ID
			try:
				# Normalize Persian/Arabic digits
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				
				if not normalized_text.isdigit():
					from src.context.messages.replies.admin_add_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				target_user_id = int(normalized_text)
				
				# Debug: Check what users exist
				all_users = await session.scalars(select(User.user_id, User.tg_name).limit(5))
				print(f"DEBUG: Looking for user_id: {target_user_id}")
				print(f"DEBUG: Sample users in DB: {list(all_users)}")
				
				# Check if user exists in database
				target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
				print(f"LOG: Looking for user_id {target_user_id}")
				print(f"LOG: Found user: {target_user}")
				
				# Also check if there are any users with this user_id
				all_users_with_id = await session.scalars(select(User).where(User.user_id == target_user_id))
				users_list = list(all_users_with_id)
				print(f"LOG: All users with this user_id: {users_list}")
				
				if not target_user:
					from src.context.messages.replies.admin_add_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				# Check if user is already admin
				existing_admin = await session.scalar(select(Admin.id).where(Admin.user_id == target_user.id))
				if existing_admin:
					from src.context.messages.replies.admin_add_confirm import get_already_admin_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_already_admin_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				# Show processing message first and reset step
				user.step = "admin_panel"
				await session.commit()
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer("⏳ در حال پردازش...", reply_markup=kb)
				
				# Show confirmation
				from src.context.messages.replies.admin_add_confirm import get_message as get_confirm_message
				from src.context.keyboards.inline.admin_add_confirm import build_keyboard as build_confirm_kb
				
				user_name = target_user.tg_name or 'نام نامشخص'
				await message.answer(get_confirm_message(user_name, target_user_id), reply_markup=build_confirm_kb(target_user_id), parse_mode="Markdown")
				return
				
			except Exception as e:
				from src.context.messages.replies.admin_add_confirm import get_user_not_found_message
				from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
				await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
				return

		# Handle admin rewards referral setting step
		if user and user.step == "admin_rewards_referral":
			# Check if user is admin
			is_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_admin = True
				else:
					if user_id:
						exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
						is_admin = bool(exists)
			except Exception:
				is_admin = False
			
			if not is_admin:
				await message.answer("❌ شما دسترسی به این بخش ندارید.")
				return
			
			# Handle back button
			from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
			back_id = resolve_back_id(text)
			if back_id == "admin_rewards:back":
				# Return to admin panel
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
				kb, _ = build_admin_kb()
				await message.answer(get_admin_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Validate and process the new amount
			try:
				# Normalize Persian/Arabic digits
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				
				if not normalized_text.isdigit():
					from src.context.messages.replies.admin_rewards_referral_success import get_invalid_amount_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_invalid_amount_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				new_amount = int(normalized_text)
				
				if new_amount < 0 or new_amount > 100000:
					from src.context.messages.replies.admin_rewards_referral_success import get_invalid_amount_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_invalid_amount_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				
				# Update the reward amount in database
				from src.databases.rewards import Reward
				reward: Reward | None = await session.scalar(select(Reward))
				if not reward:
					reward = Reward(invite_amount=new_amount)
					session.add(reward)
				else:
					reward.invite_amount = new_amount
				
				await session.commit()
				
				# Reset step and show success
				user.step = "admin_panel"
				await session.commit()
				
				from src.context.messages.replies.admin_rewards_referral_success import get_message as get_success_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
				kb, _ = build_admin_kb()
				await message.answer(get_success_message(new_amount), reply_markup=kb, parse_mode="Markdown")
				return
				
			except Exception as e:
				from src.context.messages.replies.admin_rewards_referral_success import get_invalid_amount_message
				from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
				await message.answer(get_invalid_amount_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
				return

	# Handle pricing management back button
	if text == "🔙 بازگشت" and user.step.startswith("pricing_set_"):
		print(f"LOG: Back button pressed, current step: {user.step}")
		# Reset user step to admin panel
		user.step = "admin_panel"
		await session.commit()
		print(f"LOG: Step updated to: {user.step}")
		
		# Show admin panel
		from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
		from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
		kb, _ = build_admin_panel_kb()
		await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
		return

	# Handle pricing input steps
	if user.step == "pricing_set_vip_price":
		# Validate and update VIP price
		try:
			new_price = int(text.strip())
			if 5000 <= new_price <= 10000000:
				from src.databases.products import Product
				from sqlalchemy import select, update
				product: Product | None = await session.scalar(select(Product))
				if product:
					await session.execute(
						update(Product)
						.where(Product.id == product.id)
						.values(vip_rank_price=new_price)
					)
					# Reset user step to admin panel
					print(f"LOG: Before step change - user.step: {user.step}")
					await session.execute(
						update(User)
						.where(User.id == user.id)
						.values(step="admin_panel")
					)
					await session.commit()
					print(f"LOG: Step updated in database to admin_panel")
					
					from src.context.messages.replies.pricing_set_success import get_success_message
					await message.answer(get_success_message("تعرفه رنک VIP", new_price, "price"), parse_mode="HTML")
					
					# Show admin panel
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن اطلاعات تعرفه‌ها.")
			else:
				from src.context.messages.replies.pricing_set_success import get_invalid_message
				await message.answer(get_invalid_message("price"), parse_mode="HTML")
		except ValueError:
			from src.context.messages.replies.pricing_set_success import get_invalid_message
			await message.answer(get_invalid_message("price"), parse_mode="HTML")
		return

	if user.step == "pricing_set_vip_time":
		# Validate and update VIP time
		try:
			new_time = int(text.strip())
			if 1 <= new_time <= 3650:
				from src.databases.products import Product
				from sqlalchemy import select, update
				product: Product | None = await session.scalar(select(Product))
				if product:
					await session.execute(
						update(Product)
						.where(Product.id == product.id)
						.values(vip_rank_time=new_time)
					)
					# Reset user step to admin panel
					await session.execute(
						update(User)
						.where(User.id == user.id)
						.values(step="admin_panel")
					)
					await session.commit()
					
					from src.context.messages.replies.pricing_set_success import get_success_message
					await message.answer(get_success_message("زمان رنک VIP", new_time, "time"), parse_mode="HTML")
					
					# Show admin panel
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن اطلاعات تعرفه‌ها.")
			else:
				from src.context.messages.replies.pricing_set_success import get_invalid_message
				await message.answer(get_invalid_message("time"), parse_mode="HTML")
		except ValueError:
			from src.context.messages.replies.pricing_set_success import get_invalid_message
			await message.answer(get_invalid_message("time"), parse_mode="HTML")
		return

	if user.step == "pricing_set_delete_price":
		# Validate and update delete price
		try:
			new_price = int(text.strip())
			if 5000 <= new_price <= 10000000:
				from src.databases.products import Product
				from sqlalchemy import select, update
				product: Product | None = await session.scalar(select(Product))
				if product:
					await session.execute(
						update(Product)
						.where(Product.id == product.id)
						.values(delete_account_price=new_price)
					)
					# Reset user step to admin panel
					await session.execute(
						update(User)
						.where(User.id == user.id)
						.values(step="admin_panel")
					)
					await session.commit()
					
					from src.context.messages.replies.pricing_set_success import get_success_message
					await message.answer(get_success_message("تعرفه حذف اکانت", new_price, "price"), parse_mode="HTML")
					
					# Show admin panel
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن اطلاعات تعرفه‌ها.")
			else:
				from src.context.messages.replies.pricing_set_success import get_invalid_message
				await message.answer(get_invalid_message("price"), parse_mode="HTML")
		except ValueError:
			from src.context.messages.replies.pricing_set_success import get_invalid_message
			await message.answer(get_invalid_message("price"), parse_mode="HTML")
		return

	if user.step == "pricing_set_unban_price":
		# Validate and update unban price
		try:
			new_price = int(text.strip())
			if 5000 <= new_price <= 10000000:
				from src.databases.products import Product
				from sqlalchemy import select, update
				product: Product | None = await session.scalar(select(Product))
				if product:
					await session.execute(
						update(Product)
						.where(Product.id == product.id)
						.values(unban_price=new_price)
					)
					# Reset user step to admin panel
					await session.execute(
						update(User)
						.where(User.id == user.id)
						.values(step="admin_panel")
					)
					await session.commit()
					
					from src.context.messages.replies.pricing_set_success import get_success_message
					await message.answer(get_success_message("تعرفه رفع مسدودیت", new_price, "price"), parse_mode="HTML")
					
					# Show admin panel
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن اطلاعات تعرفه‌ها.")
			else:
				from src.context.messages.replies.pricing_set_success import get_invalid_message
				await message.answer(get_invalid_message("price"), parse_mode="HTML")
		except ValueError:
			from src.context.messages.replies.pricing_set_success import get_invalid_message
			await message.answer(get_invalid_message("price"), parse_mode="HTML")
		return

	# Handle pricing management
	if text == "💳 مدیریت تعرفه ها و محصولات":
		# Check if user is admin
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.admins import Admin
		from sqlalchemy import select
		import os
		
		user_id = message.from_user.id if message.from_user else 0
		is_admin = False
		try:
			admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
			if user_id and admin_env and str(user_id) == str(admin_env):
				is_admin = True
			else:
				if user_id:
					async with get_session() as session:
						user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
						if user is not None:
							exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
							is_admin = bool(exists)
		except Exception:
			is_admin = False
		
		if not is_admin:
			await message.answer("❌ شما دسترسی به این بخش ندارید.")
			return

		# Handle support add step
		if user and user.step == "support_add":
			# Super admin only
			is_super_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_super_admin = True
			except Exception:
				is_super_admin = False
			if not is_super_admin:
				await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند پشتیبان‌ها را مدیریت کنند.")
				return

			# Handle back
			from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
			back_id = resolve_back_id(text)
			if back_id == "admin_rewards:back":
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return

			# Validate and process ID
			try:
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				if not normalized_text.isdigit():
					from src.context.messages.replies.support_add_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				target_user_id = int(normalized_text)
				from sqlalchemy import select
				target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
				if not target_user:
					from src.context.messages.replies.support_add_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				from src.databases.supporters import Supporter
				existing = await session.scalar(select(Supporter.id).where(Supporter.user_id == target_user.id))
				if existing:
					from src.context.messages.replies.support_add_confirm import get_already_support_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_already_support_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				# processing and reset step
				user.step = "admin_panel"
				await session.commit()
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer("⏳ در حال پردازش...", reply_markup=kb)
				# confirmation
				from src.context.messages.replies.support_add_confirm import get_message as get_confirm_message
				from src.context.keyboards.inline.support_add_confirm import build_keyboard as build_confirm_kb
				user_name = target_user.tg_name or 'نام نامشخص'
				await message.answer(get_confirm_message(user_name, target_user_id), reply_markup=build_confirm_kb(target_user_id), parse_mode="Markdown")
				return
			except Exception:
				from src.context.messages.replies.support_add_confirm import get_user_not_found_message
				from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
				await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
				return

		# Handle support remove step
		if user and user.step == "support_remove":
			# Super admin only
			is_super_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_super_admin = True
			except Exception:
				is_super_admin = False
			if not is_super_admin:
				await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند پشتیبان‌ها را مدیریت کنند.")
				return

			# Handle back
			from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
			back_id = resolve_back_id(text)
			if back_id == "admin_rewards:back":
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return

			# Validate and process ID
			try:
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				if not normalized_text.isdigit():
					from src.context.messages.replies.support_remove_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				target_user_id = int(normalized_text)
				from sqlalchemy import select
				target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
				if not target_user:
					from src.context.messages.replies.support_remove_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				from src.databases.supporters import Supporter
				existing = await session.scalar(select(Supporter.id).where(Supporter.user_id == target_user.id))
				if not existing:
					from src.context.messages.replies.support_remove_confirm import get_not_support_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_not_support_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return
				# processing and reset step
				user.step = "admin_panel"
				await session.commit()
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer("⏳ در حال پردازش...", reply_markup=kb)
				# confirmation
				from src.context.messages.replies.support_remove_confirm import get_message as get_confirm_message
				from src.context.keyboards.inline.support_remove_confirm import build_keyboard as build_confirm_kb
				user_name = target_user.tg_name or 'نام نامشخص'
				await message.answer(get_confirm_message(user_name, target_user_id), reply_markup=build_confirm_kb(target_user_id), parse_mode="Markdown")
				return
			except Exception:
				from src.context.messages.replies.support_remove_confirm import get_user_not_found_message
				from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
				await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
				return
		
		# Check user step
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "admin_panel":
				await message.answer("❌ شما در پنل مدیریت نیستید.")
				return
		
		# Show pricing management information (from DB)
		from sqlalchemy import select
		from src.core.database import get_session
		from src.databases.products import Product
		from src.context.messages.replies.pricing_management_welcome import get_message as get_pricing_message
		from src.context.keyboards.inline.pricing_management_menu import build_keyboard as build_pricing_menu_kb
		async with get_session() as session:
			product: Product | None = await session.scalar(select(Product))
			unban_price = int(getattr(product, "unban_price", 0)) if product else 0
			delete_price = int(getattr(product, "delete_account_price", 0)) if product else 0
			vip_price = int(getattr(product, "vip_rank_price", 0)) if product else 0
			vip_time_days = int(getattr(product, "vip_rank_time", 0)) if product else 0
		await message.answer(
			get_pricing_message(unban_price, delete_price, vip_price, vip_time_days),
			reply_markup=build_pricing_menu_kb(),
			parse_mode="HTML",
		)
		return

	# Early handle supporter steps (numeric input) regardless of admin panel buttons
	try:
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select
		user_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user and user.step in ("support_add", "support_remove"):
				# Super admin gate
				import os
				is_super_admin = False
				try:
					admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
					if user_id and admin_env and str(user_id) == str(admin_env):
						is_super_admin = True
				except Exception:
					is_super_admin = False
				if not is_super_admin:
					await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند پشتیبان‌ها را مدیریت کنند.")
					return

				# Back button
				from src.context.keyboards.reply.admin_rewards_back import resolve_id_from_text as resolve_back_id
				back_id = resolve_back_id(text)
				if back_id == "admin_rewards:back":
					user.step = "admin_panel"
					await session.commit()
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
					return

				# Validate numeric id
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				if not normalized_text.isdigit():
					if user.step == "support_add":
						from src.context.messages.replies.support_add_confirm import get_user_not_found_message
					else:
						from src.context.messages.replies.support_remove_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return

				# Keep current step before resetting later
				current_step = user.step
				target_user_id = int(normalized_text)
				target_user: User | None = await session.scalar(select(User).where(User.user_id == target_user_id))
				if not target_user:
					if user.step == "support_add":
						from src.context.messages.replies.support_add_confirm import get_user_not_found_message
					else:
						from src.context.messages.replies.support_remove_confirm import get_user_not_found_message
					from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
					await message.answer(get_user_not_found_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
					return

				from src.databases.supporters import Supporter
				if user.step == "support_add":
					existing = await session.scalar(select(Supporter.id).where(Supporter.user_id == target_user.id))
					if existing:
						from src.context.messages.replies.support_add_confirm import get_already_support_message
						from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
						await message.answer(get_already_support_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
						return
				else:
					existing = await session.scalar(select(Supporter.id).where(Supporter.user_id == target_user.id))
					if not existing:
						from src.context.messages.replies.support_remove_confirm import get_not_support_message
						from src.context.keyboards.reply.admin_rewards_back import build_keyboard as build_back_kb
						await message.answer(get_not_support_message(), reply_markup=build_back_kb(), parse_mode="Markdown")
						return

				# Reset to admin_panel and show processing
				user.step = "admin_panel"
				await session.commit()
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer("⏳ در حال پردازش...", reply_markup=kb)

				# Show confirmation inline based on original step
				user_name = target_user.tg_name or 'نام نامشخص'
				if current_step == "support_add":
					from src.context.messages.replies.support_add_confirm import get_message as get_confirm_message
					from src.context.keyboards.inline.support_add_confirm import build_keyboard as build_confirm_kb
					await message.answer(get_confirm_message(user_name, target_user_id), reply_markup=build_confirm_kb(target_user_id), parse_mode="Markdown")
					return
				else:
					from src.context.messages.replies.support_remove_confirm import get_message as get_confirm_message
					from src.context.keyboards.inline.support_remove_confirm import build_keyboard as build_confirm_kb
					await message.answer(get_confirm_message(user_name, target_user_id), reply_markup=build_confirm_kb(target_user_id), parse_mode="Markdown")
					return
	except Exception:
		pass

	# Handle admin management
	if text == "👑 مدیریت ادمین ها":
		# Check if user is super admin (only super admins can manage admins)
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select
		import os
		
		user_id = message.from_user.id if message.from_user else 0
		is_super_admin = False
		try:
			admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
			if user_id and admin_env and str(user_id) == str(admin_env):
				is_super_admin = True
		except Exception:
			is_super_admin = False
		
		if not is_super_admin:
			await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند ادمین‌ها را مدیریت کنند.")
			return
		
		# Check user step
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "admin_panel":
				await message.answer("❌ شما در پنل مدیریت نیستید.")
				return
		
		# Get admins list and show management interface
		from src.services.admin_list_service import get_admins_list
		from src.context.messages.replies.admin_management_welcome import get_message as get_admin_message
		from src.context.keyboards.inline.admin_management_menu import build_keyboard as build_admin_kb
		
		admins_list = await get_admins_list()
		await message.answer(get_admin_message(admins_list), reply_markup=build_admin_kb(), parse_mode="Markdown")
		return

	# Handle support management
	if text == "🛟 مدیریت پشتیبان ها":
		# Check if user is super admin
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select
		import os

		user_id = message.from_user.id if message.from_user else 0
		is_super_admin = False
		try:
			admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
			if user_id and admin_env and str(user_id) == str(admin_env):
				is_super_admin = True
		except Exception:
			is_super_admin = False

		if not is_super_admin:
			await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند پشتیبان‌ها را مدیریت کنند.")
			return

		# Check user step
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "admin_panel":
				await message.answer("❌ شما در پنل مدیریت نیستید.")
				return

		# Get supporters list and show management interface
		from src.services.supporter_list_service import get_supporters_list
		from src.context.messages.replies.support_management_welcome import get_message as get_support_message
		from src.context.keyboards.inline.support_management_menu import build_keyboard as build_support_kb

		supporters_list = await get_supporters_list()
		await message.answer(get_support_message(supporters_list), reply_markup=build_support_kb(), parse_mode="Markdown")
		return

	# Handle bot settings steps (name/main/support/cache) and back button
	from src.core.database import get_session
	from sqlalchemy import select, update
	from src.context.keyboards.reply.bot_settings_back import resolve_id_from_text as resolve_bot_back
	from src.databases.users import User as _UserForBotSettings
	from src.databases.bot_settings import BotSetting as _BotSetting
	async with get_session() as session:
		user: _UserForBotSettings | None = await session.scalar(select(_UserForBotSettings).where(_UserForBotSettings.user_id == (message.from_user.id if message.from_user else 0)))
		if user and user.step and user.step.startswith("bot_settings_"):
			# Back button
			bot_back = resolve_bot_back(text)
			if bot_back == "bot_settings:back":
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
				kb, _ = build_admin_kb()
				await message.answer(get_admin_message(), reply_markup=kb, parse_mode="Markdown")
				return

			# Name update
			if user.step == "bot_settings_bot_name":
				new_name = text.strip()
				if not new_name or len(new_name) > 255:
					await message.answer("❌ نام نامعتبر است. حداکثر 255 کاراکتر و خالی نباشد.")
					return
				settings = await session.scalar(select(_BotSetting))
				if settings:
					await session.execute(
						update(_BotSetting).where(_BotSetting.id == settings.id).values(bot_name=new_name)
					)
					user.step = "admin_panel"
					await session.commit()
					await message.answer("✅ نام ربات با موفقیت به‌روزرسانی شد.")
					from src.context.messages.replies.admin_panel_welcome import get_message as _get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as _build_admin_panel_kb
					kb, _ = _build_admin_panel_kb()
					await message.answer(_get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن تنظیمات ربات.")
				return

			# Main channel update
			if user.step == "bot_settings_main_channel":
				username = text.strip().lstrip('@')
				if not username or len(username) < 5 or len(username) > 32 or not all(c.isalnum() or c == '_' for c in username):
					await message.answer(
						"❌ نام کاربری کانال نامعتبر است.\n\n"
						"• طول 5 تا 32 کاراکتر\n"
						"• فقط حروف، اعداد و _\n"
					)
					return
				settings = await session.scalar(select(_BotSetting))
				if settings:
					await session.execute(
						update(_BotSetting).where(_BotSetting.id == settings.id).values(bot_channel=username)
					)
					user.step = "admin_panel"
					await session.commit()
					await message.answer("✅ کانال اصلی با موفقیت به‌روزرسانی شد.")
					from src.context.messages.replies.admin_panel_welcome import get_message as _get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as _build_admin_panel_kb
					kb, _ = _build_admin_panel_kb()
					await message.answer(_get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن تنظیمات ربات.")
				return

			# Support channel update
			if user.step == "bot_settings_support_channel":
				username = text.strip().lstrip('@')
				if not username or len(username) < 5 or len(username) > 32 or not all(c.isalnum() or c == '_' for c in username):
					await message.answer(
						"❌ نام کاربری پشتیبانی نامعتبر است.\n\n"
						"• طول 5 تا 32 کاراکتر\n"
						"• فقط حروف، اعداد و _\n"
					)
					return
				settings = await session.scalar(select(_BotSetting))
				if settings:
					await session.execute(
						update(_BotSetting).where(_BotSetting.id == settings.id).values(bot_support_username=username)
					)
					user.step = "admin_panel"
					await session.commit()
					await message.answer("✅ کانال پشتیبانی با موفقیت به‌روزرسانی شد.")
					from src.context.messages.replies.admin_panel_welcome import get_message as _get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as _build_admin_panel_kb
					kb, _ = _build_admin_panel_kb()
					await message.answer(_get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن تنظیمات ربات.")
				return

			# Cache channel update
			if user.step == "bot_settings_cache_channel":
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				cleaned_text = ''.join(c for c in normalized_text if c.isdigit() or c == '-')
				if not cleaned_text or not cleaned_text.lstrip('-').isdigit():
					await message.answer(
						"❌ آیدی کانال نامعتبر است!\n\n"
						"لطفاً آیدی کانال را به صورت عددی ارسال کنید:\n"
						"• مثال: -1001234567890\n"
						"• برای لغو عملیات 'بازگشت' را ارسال کنید"
					)
					return
				new_channel_id = int(cleaned_text)
				settings = await session.scalar(select(_BotSetting))
				if settings:
					await session.execute(
						update(_BotSetting).where(_BotSetting.id == settings.id).values(cache_channel_id=new_channel_id)
					)
					await session.commit()
					user.step = "admin_panel"
					await session.commit()
					await message.answer(
						f"✅ کانال کش با موفقیت به‌روزرسانی شد!\n\n"
						f"آیدی کانال جدید: {new_channel_id}",
						parse_mode="Markdown"
					)
					from src.context.messages.replies.admin_panel_welcome import get_message as _get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as _build_admin_panel_kb
					kb, _ = _build_admin_panel_kb()
					await message.answer(_get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن تنظیمات ربات.")
				return

		# Handle financial search (must be before admin panel buttons)
		if user.step == "financial_search":
			# Handle back button - check for exact match first
			if text.strip() == "🔙 بازگشت" or text.strip().lower() in ["بازگشت", "back", "لغو", "cancel"]:
				# Return to admin panel
				user.step = "admin_panel"
				await session.commit()
				
				# Show admin panel
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Handle search query
			from src.handlers.callbacks.financial_management import handle_payment_search
			await handle_payment_search(message, text.strip())
			return

		# Handle user search (must be before admin panel buttons)
		if user.step == "user_search":
			# Handle back button - check for exact match first
			if text.strip() == "🔙 بازگشت" or text.strip().lower() in ["بازگشت", "back", "لغو", "cancel"]:
				# Return to admin panel
				user.step = "admin_panel"
				await session.commit()
				
				# Show admin panel
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Handle search query
			from src.handlers.callbacks.user_management import handle_user_search
			await handle_user_search(message, text.strip())
			return

		# Handle user profile report write flow (must be before admin panel buttons)
		if user.step.startswith("report_write:"):
			# Back button
			if text.strip() in ("🔙 بازگشت", "بازگشت 🔙") or text.strip().lower() in ("بازگشت", "back", "لغو", "cancel"):
				# Clear step and show start message with main buttons
				user.step = ""
				await session.commit()
				from src.context.messages.commands.start import get_message as get_start_message
				from src.context.keyboards.reply.mainButtons import build_keyboard_for
				name = None
				if message.from_user:
					name = message.from_user.first_name or message.from_user.username or None
				text_start = await get_start_message(name)
				kb_start, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
				await message.answer(text_start, reply_markup=kb_start, parse_mode="Markdown")
				return

			# Persist report to database
			from sqlalchemy import insert, select
			from src.databases.reports import Report
			from datetime import datetime

			parts = user.step.split(":", 2)
			# format: report_write:{unique_id}:{category}
			_, unique_id, category_value = (parts + ["", ""])[:3]
			# Resolve viewer and target ids
			target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
			if not target:
				await message.answer("❌ کاربر مورد نظر یافت نشد.")
				user.step = ""
				await session.commit()
				return
			category_id = None if category_value == "other" else int(category_value)
			# Insert report and get the ID
			result = await session.execute(
				insert(Report).values(
					category_id=category_id,
					user_id=user.id,
					target_id=target.id,
					reason=text.strip(),
					approved_at=None,
					rejected_at=None,
					created_at=datetime.utcnow(),
				)
			)
			report_id = result.inserted_primary_key[0]
			user.step = ""
			await session.commit()
			
			# Send confirmation to reporter
			await message.answer("✅ گزارش شما دریافت شد و در حال بررسی است.")
			
			# Send notification to all admins and supporters
			from src.databases.admins import Admin
			from src.databases.supporters import Supporter
			from src.context.messages.notifications.report_notification import get_message as get_notification_message
			from src.context.keyboards.inline.report_actions import build_keyboard as build_actions_kb
			
			# Get reporter and target names
			reporter_name = message.from_user.first_name or message.from_user.username or "نامشخص"
			target_name = target.tg_name or "نامشخص"
			category_name = "سایر موارد" if category_value == "other" else "دسته‌بندی مشخص نشده"
			
			# Get category name if not "other"
			if category_value != "other":
				from src.databases.report_categories import ReportCategory
				category_obj = await session.scalar(select(ReportCategory).where(ReportCategory.id == category_id))
				if category_obj:
					category_name = category_obj.subject
			
			notification_text = get_notification_message(
				reporter_name=reporter_name,
				reporter_id=message.from_user.id if message.from_user else 0,
				target_name=target_name,
				target_id=target.user_id,
				target_unique_id=target.unique_id,
				category=category_name,
				reason=text.strip()
			)
			actions_kb = build_actions_kb(report_id)
			
			# Collect all unique notification recipients
			import os
			notification_recipients = set()
			
			# Add super admin from .env
			super_admin_id = os.getenv("TELEGRAM_ADMIN_USER_ID")
			if super_admin_id:
				notification_recipients.add(int(super_admin_id))
			
			# Add all admins
			admin_results = await session.execute(
				select(Admin, User)
				.join(User, Admin.user_id == User.id)
			)
			for admin, admin_user in admin_results:
				notification_recipients.add(admin_user.user_id)
			
			# Add all supporters
			supporter_results = await session.execute(
				select(Supporter, User)
				.join(User, Supporter.user_id == User.id)
			)
			for supporter, supporter_user in supporter_results:
				notification_recipients.add(supporter_user.user_id)
			
			# Send notification to each unique recipient
			for user_id in notification_recipients:
				try:
					await message.bot.send_message(
						chat_id=user_id,
						text=notification_text,
						reply_markup=actions_kb,
						parse_mode="HTML"
					)
					print(f"LOG: Report notification sent to user {user_id}")
				except Exception as e:
					print(f"LOG: Failed to send report notification to user {user_id}: {e}")
			
			# Then show Start message with main buttons
			from src.context.messages.commands.start import get_message as get_start_message
			from src.context.keyboards.reply.mainButtons import build_keyboard_for
			name = None
			if message.from_user:
				name = message.from_user.first_name or message.from_user.username or None
			text_start = await get_start_message(name)
			kb_start, _ = await build_keyboard_for(message.from_user.id if message.from_user else None)
			await message.answer(text_start, reply_markup=kb_start, parse_mode="Markdown")
			return

		# Handle punishment user step (admin punishment flow)
		if user.step.startswith("punish_user:"):
			# Back button
			if text.strip() in ("🔙 بازگشت", "بازگشت 🔙", "لغو مجازات 🔙") or text.strip().lower() in ("بازگشت", "back", "لغو", "cancel"):
				# Clear step and show admin panel
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				return

			# Validate and process punishment days
			try:
				days = int(text.strip())
				if not (1 <= days <= 365):
					await message.answer("❌ تعداد روزها باید بین 1 تا 365 باشد. لطفاً مجدداً وارد کنید:")
					return
			except ValueError:
				await message.answer("❌ لطفاً یک عدد معتبر وارد کنید (1-365):")
				return

			# Get target user ID from step
			parts = user.step.split(":", 1)
			target_user_id = int(parts[1]) if len(parts) > 1 else None
			
			if target_user_id:
				# Get target user
				target_user = await session.scalar(select(User).where(User.id == target_user_id))
				if target_user:
					# Create ban record
					from src.databases.user_bans import UserBan
					from datetime import datetime, timedelta
					
					ban_until = datetime.utcnow() + timedelta(days=days)
					ban_record = UserBan(
						user_id=target_user.id,
						expiry=ban_until
					)
					session.add(ban_record)
					await session.commit()
					
					# Send confirmation to admin
					confirmation_text = (
						f"✅ کاربر مسدود شد!\n\n"
						f"👤 <b>کاربر مسدود شده:</b>\n"
						f"🆔 آیدی: {target_user.user_id}\n"
						f"📛 نام کاربری: {target_user.tg_name or 'نامشخص'}\n"
						f"⏰ مدت مسدودیت: {days} روز\n"
						f"📅 تا تاریخ: {ban_until.strftime('%Y-%m-%d %H:%M')}"
					)
					
					# Clear step and show admin panel
					user.step = "admin_panel"
					await session.commit()
					
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					
					await message.answer(confirmation_text, reply_markup=kb, parse_mode="HTML")
					return
			
			# If we get here, something went wrong
			user.step = "admin_panel"
			await session.commit()
			await message.answer("❌ خطا در پردازش مجازات. به پنل مدیریت بازگشتید.")
			return

	# Handle admin panel buttons
	from src.context.keyboards.reply.admin_panel import resolve_id_from_text as resolve_admin_id
	admin_id = resolve_admin_id(text)
	if admin_id:
		from src.core.database import get_session
		from src.databases.users import User
		from src.databases.admins import Admin
		from sqlalchemy import select
		import os

		user_id = message.from_user.id if message.from_user else 0
		# Check if user is admin
		is_admin = False
		try:
			admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
			if user_id and admin_env and str(user_id) == str(admin_env):
				is_admin = True
			else:
				if user_id:
					async with get_session() as session:
						user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
						if user is not None:
							exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
							is_admin = bool(exists)
		except Exception:
			is_admin = False
		
		if not is_admin:
			from src.context.messages.replies.admin_panel_buttons import get_access_denied_message
			await message.answer(get_access_denied_message())
			return

		# Check user step
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user or user.step != "admin_panel":
				return

		# Handle admin panel buttons
		if admin_id == "admin:exit":
			# Exit admin panel - reset step to start and show main keyboard
			async with get_session() as session:
				user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
				if user:
					user.step = "start"
					await session.commit()
			
			# Send main keyboard
			from src.context.keyboards.reply.mainButtons import build_keyboard_for
			from src.context.messages.commands.start import get_message as get_start_message
			from src.context.messages.commands.panel_exit import get_message as get_exit_message
			kb, _ = await build_keyboard_for(user_id)
			name = message.from_user.first_name if message.from_user else None
			start_text = get_start_message(name)
			await message.answer(get_exit_message(), reply_markup=kb, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True))
			return
		
		# Handle rewards management
		if admin_id == "admin:rewards_management":
			from src.context.messages.replies.admin_rewards_menu import get_message as get_rewards_message
			from src.context.keyboards.inline.admin_rewards_menu import build_keyboard as build_rewards_kb
			await message.answer(get_rewards_message(), reply_markup=build_rewards_kb(), parse_mode="Markdown")
			return
		
		# Handle support management direct entry
		if admin_id == "admin:support_management":
			from src.handlers.callbacks.support_management_entry import show_support_management
			await show_support_management(message)
			return

		# Handle bot settings
		if admin_id == "admin:bot_settings":
			from src.handlers.callbacks.bot_settings_entry import show_bot_settings
			await show_bot_settings(message)
			return

		# Handle financial management
		if admin_id == "admin:financial_management":
			from src.handlers.callbacks.financial_management_entry import show_financial_management
			await show_financial_management(message)
			return

		# Handle back button for bot settings steps
		from src.context.keyboards.reply.bot_settings_back import resolve_id_from_text as resolve_bot_back
		bot_back = resolve_bot_back(text)
		if bot_back == "bot_settings:back" and user and user.step and user.step.startswith("bot_settings_"):
			# Return to admin panel
			user.step = "admin_panel"
			await session.commit()
			from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_message
			from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
			kb, _ = build_admin_kb()
			await message.answer(get_admin_message(), reply_markup=kb, parse_mode="Markdown")
			return

		# Handle bot name input
		if user and user.step == "bot_settings_bot_name":
			# Simple length validation
			new_name = text.strip()
			if not new_name or len(new_name) > 255:
				await message.answer("❌ نام نامعتبر است. حداکثر 255 کاراکتر و خالی نباشد.")
				return
			from src.databases.bot_settings import BotSetting
			from sqlalchemy import update
			settings = await session.scalar(select(BotSetting))
			if settings:
				await session.execute(
					update(BotSetting)
					.where(BotSetting.id == settings.id)
					.values(bot_name=new_name)
				)
				# Reset step and show success
				user.step = "admin_panel"
				await session.commit()
				await message.answer("✅ نام ربات با موفقیت به‌روزرسانی شد.")
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
			else:
				await message.answer("❌ خطا در یافتن تنظیمات ربات.")
			return

		# Handle main channel username input
		if user and user.step == "bot_settings_main_channel":
			username = text.strip().lstrip('@')
			if not username or len(username) < 5 or len(username) > 32 or not all(c.isalnum() or c == '_' for c in username):
				await message.answer(
					"❌ نام کاربری کانال نامعتبر است.\n\n"
					"• طول 5 تا 32 کاراکتر\n"
					"• فقط حروف، اعداد و _\n"
				)
				return
			from src.databases.bot_settings import BotSetting
			from sqlalchemy import update
			settings = await session.scalar(select(BotSetting))
			if settings:
				await session.execute(
					update(BotSetting)
					.where(BotSetting.id == settings.id)
					.values(bot_channel=username)
				)
				user.step = "admin_panel"
				await session.commit()
				await message.answer("✅ کانال اصلی با موفقیت به‌روزرسانی شد.")
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
			else:
				await message.answer("❌ خطا در یافتن تنظیمات ربات.")
			return

		# Handle support channel username input
		if user and user.step == "bot_settings_support_channel":
			username = text.strip().lstrip('@')
			if not username or len(username) < 5 or len(username) > 32 or not all(c.isalnum() or c == '_' for c in username):
				await message.answer(
					"❌ نام کاربری پشتیبانی نامعتبر است.\n\n"
					"• طول 5 تا 32 کاراکتر\n"
					"• فقط حروف، اعداد و _\n"
				)
				return
			from src.databases.bot_settings import BotSetting
			from sqlalchemy import update
			settings = await session.scalar(select(BotSetting))
			if settings:
				await session.execute(
					update(BotSetting)
					.where(BotSetting.id == settings.id)
					.values(bot_support_username=username)
				)
				user.step = "admin_panel"
				await session.commit()
				await message.answer("✅ کانال پشتیبانی با موفقیت به‌روزرسانی شد.")
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
				kb, _ = build_admin_panel_kb()
				await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
			else:
				await message.answer("❌ خطا در یافتن تنظیمات ربات.")
			return

		# Handle cache channel setting step
		if user and user.step == "bot_settings_cache_channel":
			# Check if user is admin
			is_admin = False
			try:
				admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
				if user_id and admin_env and str(user_id) == str(admin_env):
					is_admin = True
				else:
					if user_id:
						from src.databases.admins import Admin
						exists = await session.scalar(select(Admin.id).where(Admin.user_id == user.id))
						is_admin = bool(exists)
			except Exception:
				is_admin = False
			
			if not is_admin:
				await message.answer("❌ شما دسترسی به این بخش ندارید.")
				return
			
			# Handle back button
			if text.strip().lower() in ["بازگشت", "back", "لغو", "cancel"]:
				# Return to admin panel
				user.step = "admin_panel"
				await session.commit()
				from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_message
				from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
				kb, _ = build_admin_kb()
				await message.answer(get_admin_message(), reply_markup=kb, parse_mode="Markdown")
				return
			
			# Validate and process the new cache channel ID
			try:
				# Normalize Persian/Arabic digits
				from src.middlewares.profile_middleware import _normalize_digits
				normalized_text = _normalize_digits(text.strip())
				
				# Remove any non-digit characters except minus sign
				cleaned_text = ''.join(c for c in normalized_text if c.isdigit() or c == '-')
				
				if not cleaned_text or not cleaned_text.lstrip('-').isdigit():
					await message.answer(
						"❌ آیدی کانال نامعتبر است!\n\n"
						"لطفاً آیدی کانال را به صورت عددی ارسال کنید:\n"
						"• مثال: -1001234567890\n"
						"• برای لغو عملیات 'بازگشت' را ارسال کنید"
					)
					return
				
				new_channel_id = int(cleaned_text)
				
				# Update bot settings
				from src.databases.bot_settings import BotSetting
				from sqlalchemy import update
				
				settings = await session.scalar(select(BotSetting))
				if settings:
					await session.execute(
						update(BotSetting)
						.where(BotSetting.id == settings.id)
						.values(cache_channel_id=new_channel_id)
					)
					await session.commit()
					
					# Reset user step to admin panel
					user.step = "admin_panel"
					await session.commit()
					
					# Show success message and admin panel
					await message.answer(
						f"✅ کانال کش با موفقیت به‌روزرسانی شد!\n\n"
						f"آیدی کانال جدید: {new_channel_id}",
						parse_mode="Markdown"
					)
					
					# Show admin panel
					from src.context.messages.replies.admin_panel_welcome import get_message as get_admin_panel_message
					from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_panel_kb
					kb, _ = build_admin_panel_kb()
					await message.answer(get_admin_panel_message(), reply_markup=kb, parse_mode="Markdown")
				else:
					await message.answer("❌ خطا در یافتن تنظیمات ربات.")
			except ValueError:
				await message.answer(
					"❌ آیدی کانال نامعتبر است!\n\n"
					"لطفاً آیدی کانال را به صورت عددی ارسال کنید:\n"
					"• مثال: -1001234567890\n"
					"• برای لغو عملیات 'بازگشت' را ارسال کنید"
				)
			return

		# Handle chat management
		if admin_id == "admin:chat_management":
			from src.handlers.callbacks.chat_management_entry import show_chat_management
			await show_chat_management(message)
			return

		# Handle user management
		if admin_id == "admin:user_management":
			from src.handlers.callbacks.user_management_entry import show_user_management
			await show_user_management(message)
			return

		# Handle statistics
		if admin_id == "admin:statistics":
			from src.handlers.callbacks.statistics_entry import show_statistics
			await show_statistics(message)
			return

		# Handle other admin panel buttons (placeholder for now)
		if admin_id in ["admin:financial_management", "admin:reports_management", "admin:pricing_management", "admin:admin_management"]:
			from src.context.messages.replies.admin_panel_buttons import get_development_message
			await message.answer(get_development_message(admin_id))
			return

	await message.answer("🔸 متوجه نشدم چی میخوای 🙃\n\nاگر نیاز به کمک داری دستور /help رو بفرست")


