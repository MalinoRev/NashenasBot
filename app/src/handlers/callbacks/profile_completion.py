from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_locations import UserLocation


async def handle_profile_completion(callback: CallbackQuery) -> None:
	user_id = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or getattr(user, "step", "start") != "start":
			await callback.answer()
			return
		# Determine missing pieces: photo first, then location
		# Photo considered complete if custom avatar exists
		custom_photo_exists = False
		try:
			from pathlib import Path
			avatar_dirs = [
				(Path("storage") / "avatars").resolve(),
				(Path("src") / "storage" / "avatars").resolve(),
			]
			for avatars_dir in avatar_dirs:
				for p in [avatars_dir / f"{user.id}.jpg", avatars_dir / f"{user.id}.jpeg", avatars_dir / f"{user.id}.png"]:
					if p.exists():
						custom_photo_exists = True
						break
				if custom_photo_exists:
					break
		except Exception:
			custom_photo_exists = False

		if not custom_photo_exists:
			# Route to photo edit flow
			from src.handlers.callbacks.profile_edit_photo import handle_profile_edit_photo
			await handle_profile_edit_photo(callback)
			return

		# Else check location
		location_exists = bool(
			await session.scalar(select(UserLocation.id).where(UserLocation.user_id == user.id))
		)
		if not location_exists:
			# Route to location sending flow
			from src.handlers.callbacks.nearby_request_location import handle_nearby_request_location
			await handle_nearby_request_location(callback)
			return

	# Nothing missing
	await callback.answer("پروفایل شما کامل است.")


