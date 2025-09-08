import secrets
import string
from typing import Any, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_settings import UserSetting
from src.context.messages.auth.welcome import get_message as get_welcome_message


class AuthMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		user_id: Optional[int] = None
		tg_name: Optional[str] = None

		if isinstance(event, Message):
			if event.from_user:
				user_id = event.from_user.id
				tg_name = event.from_user.username or event.from_user.full_name
		elif isinstance(event, CallbackQuery):
			if event.from_user:
				user_id = event.from_user.id
				tg_name = event.from_user.username or event.from_user.full_name

		# Authenticate: ensure user exists; create if missing
		if not user_id:
			data["auth_ok"] = False
			return None

		async with get_session() as session:
			existing_user = await session.scalar(select(User).where(User.user_id == user_id))
			if existing_user:
				# Check if user has settings record, create if missing
				settings = await session.scalar(select(UserSetting).where(UserSetting.user_id == existing_user.id))
				if not settings:
					# Create default settings for existing user
					default_settings = UserSetting(
						user_id=existing_user.id,
						silented_until=None,
						profile_visit_alarm=False,
						profile_like_alarm=False,
						can_get_likes=True
					)
					session.add(default_settings)
					await session.commit()
					print(f"LOG: Created default settings for existing user {existing_user.id}")
				
				data["auth_ok"] = True
				return await handler(event, data)

		# Check for referral from start payload (only for new users)
		referraled_by = None
		if isinstance(event, Message) and event.text:
			# Check if message starts with /start and has payload
			if event.text.startswith("/start "):
				start_payload = event.text.split(" ", 1)[1]  # Get part after /start
				print(f"LOG: Found start_payload: '{start_payload}'")

				# Check if payload starts with "inv_"
				if start_payload.startswith("inv_"):
					referral_code = start_payload[4:]  # Remove "inv_" prefix
					print(f"LOG: Extracted referral_code: '{referral_code}'")

					# Find referrer by referral_id (reuse existing session)
					referrer = await session.scalar(
						select(User.id).where(User.referral_id == referral_code)
					)
					if referrer:
						referraled_by = referrer
						print(f"LOG: Found referrer with id: {referrer}")
					else:
						print(f"LOG: No referrer found with referral_code: '{referral_code}'")

		# Create new user record
		alphabet = string.ascii_letters + string.digits
		uid = "".join(secrets.choice(alphabet) for _ in range(12))
		ref_id = "".join(secrets.choice(alphabet) for _ in range(12))
		name_value = tg_name or ""
		new_user = User(
			user_id=user_id,
			tg_name=name_value,
			unique_id=uid,
			referral_id=ref_id,
			referraled_queue=referraled_by,
			step="start",
		)
		try:
			async with get_session() as session2:
				session2.add(new_user)
				await session2.commit()
		except IntegrityError:
			# Concurrent create; consider authenticated
			data["auth_ok"] = True
			return await handler(event, data)
		# Created successfully
		data["auth_ok"] = True
		# Send welcome message only on Message events
		if isinstance(event, Message):
			try:
				first_name = event.from_user.first_name if event.from_user else None
				await event.answer(await get_welcome_message(first_name))
			except Exception:
				pass
		return await handler(event, data)


