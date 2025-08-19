from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like
from src.databases.user_locations import UserLocation
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb
from src.context.messages.visitor.profile_view import get_not_found_message, format_caption
from src.context.keyboards.inline.visitor_profile import build_keyboard as build_visitor_kb


class VisitorMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Only messages with text commands like /user_XXXX
		if not isinstance(event, Message):
			return await handler(event, data)
		text = (event.text or "").strip()
		if not text.startswith("/user_"):
			return await handler(event, data)
		unique_id = text.split("/user_", 1)[1].split()[0]
		# Resolve target user by unique_id
		async with get_session() as session:
			target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
			if target is None:
				kb, _ = build_main_kb()
				await event.answer(get_not_found_message(), reply_markup=kb)
				return None
			profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == target.id))
			likes_count = int((await session.scalar(select(func.count(Like.id)).where(Like.target_id == target.id))) or 0)
			# Caption parts
			name = (profile.name if profile and profile.name else None) or (target.tg_name or "بدون نام")
			age = str(profile.age) if profile and profile.age is not None else "?"
			gender_text = "دختر" if profile and profile.is_female else ("پسر" if profile and profile and profile.is_female is not None else "نامشخص")
			from src.databases.states import State
			from src.databases.cities import City
			state_name = "—"
			city_name = "—"
			if profile and profile.state is not None:
				state_val = await session.scalar(select(State.state_name).where(State.id == profile.state))
				if state_val:
					state_name = state_val
			if profile and profile.city is not None:
				city_val = await session.scalar(select(City.city_name).where(City.id == profile.city))
				if city_val:
					city_name = city_val
			# Distance from me if I have location and target has location
			distance_str = "نامشخص"
			try:
				from src.services.nearby_search import _haversine_km  # type: ignore
			except Exception:
				_haversine_km = None  # type: ignore
			me: User | None = None
			me_loc: UserLocation | None = None
			t_loc: UserLocation | None = None
			viewer_id = event.from_user.id if event.from_user else 0
			me = await session.scalar(select(User).where(User.user_id == viewer_id))
			if me:
				me_loc = await session.scalar(select(UserLocation).where(UserLocation.user_id == me.id))
			t_loc = await session.scalar(select(UserLocation).where(UserLocation.user_id == target.id))
			if _haversine_km and me_loc and t_loc and me_loc.location_x is not None and t_loc.location_x is not None:
				d = _haversine_km(me_loc.location_x, me_loc.location_y, t_loc.location_x, t_loc.location_y)
				distance_str = f"{int(round(d))}KM"
			# Like button state: whether me liked target
			liked = False
			if me:
				liked = bool(await session.scalar(select(func.count(Like.id)).where(Like.user_id == me.id, Like.target_id == target.id)))
			like_emoji = "❤️" if liked else "🤍"
			caption = format_caption(
				name=name,
				gender_text=gender_text,
				state_name=state_name,
				city_name=city_name,
				age=age,
				unique_id=unique_id,
				distance_text=distance_str,
				last_activity=getattr(target, "last_activity", None),
			)
			# Photo resolution (same logic as profile)
			from pathlib import Path
			avatar_dirs = [(Path("storage") / "avatars").resolve(), (Path("src") / "storage" / "avatars").resolve()]
			photo_path = None
			for avatars_dir in avatar_dirs:
				candidates = [avatars_dir / f"{target.id}.jpg", avatars_dir / f"{target.id}.jpeg", avatars_dir / f"{target.id}.png"]
				custom_path = next((p for p in candidates if p.exists()), None)
				if custom_path is None and avatars_dir.exists():
					for p in avatars_dir.glob(f"{target.id}.*"):
						custom_path = p
						break
				if custom_path is not None and custom_path.exists():
					photo_path = str(custom_path.resolve())
					break
			if not photo_path:
				photo_path = "src/context/resources/images/noimage-girl.jpg" if (profile and profile.is_female) else "src/context/resources/images/noimage-boy.jpg"
			# Inline keyboard for actions
			from src.databases.user_blocked import UserBlocked
			from src.databases.contacts import Contact
			is_blocked = False
			if me:
				is_blocked = bool(await session.scalar(select(func.count(UserBlocked.id)).where(UserBlocked.user_id == me.id, UserBlocked.target_id == target.id)))
			in_contacts = False
			if me:
				in_contacts = bool(await session.scalar(select(func.count(Contact.id)).where(Contact.user_id == me.id, Contact.target_id == target.id)))
			kb_inline = build_visitor_kb(unique_id=unique_id, liked=liked, likes_count=likes_count, is_blocked=is_blocked, in_contacts=in_contacts)
			# Send
			file = FSInputFile(photo_path)
			await event.answer_photo(file, caption=caption, reply_markup=kb_inline)
			return None
		# Fallback to next
		return await handler(event, data)


