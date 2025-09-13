from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, update

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.user_rewards import UserReward
from src.databases.rewards import Reward
from src.context.messages.rewards.profile_completion_success import (
	format_message as format_reward_message,
)
from pathlib import Path
from src.databases.user_locations import UserLocation


class ProfileCompletionMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Run after other middlewares and before handlers; only proceed if authenticated
		if not data.get("auth_ok"):
			return await handler(event, data)

		telegram_user_id = None
		if isinstance(event, (Message, CallbackQuery)) and event.from_user:
			telegram_user_id = event.from_user.id
		if telegram_user_id is None:
			return await handler(event, data)

		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == telegram_user_id))
			if not user:
				return await handler(event, data)

			profile: UserProfile | None = await session.scalar(
				select(UserProfile).where(UserProfile.user_id == user.id)
			)
			# Check profile completion
			is_complete = bool(
				profile
				and profile.name is not None
				and profile.is_female is not None
				and profile.age is not None
				and profile.state is not None
				and profile.city is not None
			)
			if not is_complete:
				return await handler(event, data)

			# Extra condition: user must have an uploaded avatar file
			avatar_dirs = [
				(Path("storage") / "avatars").resolve(),
				(Path("src") / "storage" / "avatars").resolve(),
			]
			avatar_ok = False
			for avatars_dir in avatar_dirs:
				candidates = [
					avatars_dir / f"{user.id}.jpg",
					avatars_dir / f"{user.id}.jpeg",
					avatars_dir / f"{user.id}.png",
				]
				custom_path = next((p for p in candidates if p.exists()), None)
				if custom_path is None and avatars_dir.exists():
					for p in avatars_dir.glob(f"{user.id}.*"):
						custom_path = p
						break
				if custom_path is not None and custom_path.exists():
					avatar_ok = True
					break
			if not avatar_ok:
				return await handler(event, data)

			# Extra condition: user must have a saved location
			location_row = await session.scalar(select(UserLocation.id).where(UserLocation.user_id == user.id))
			if not location_row:
				return await handler(event, data)

			# Check if user has already received the profile completion reward
			user_reward: UserReward | None = await session.scalar(
				select(UserReward).where(UserReward.user_id == user.id)
			)
			received = bool(user_reward and user_reward.received_profile)
			if received:
				return await handler(event, data)

			# Read reward amount (single-row table)
			reward: Reward | None = await session.scalar(select(Reward))
			bonus = int(getattr(reward, "profile_amount", 0)) if reward else 0
			if bonus > 0:
				# Add to user credit
				user.credit = int(user.credit or 0) + bonus
				# Upsert user_rewards
				if user_reward is None:
					user_reward = UserReward(user_id=user.id, received_profile=True)
					session.add(user_reward)
				else:
					user_reward.received_profile = True
				await session.commit()
				# Notify user
				if isinstance(event, Message):
					await event.answer(format_reward_message(bonus))
				elif isinstance(event, CallbackQuery) and event.message:
					await event.message.answer(format_reward_message(bonus))

		return await handler(event, data)


