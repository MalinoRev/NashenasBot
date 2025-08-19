from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, FSInputFile, LinkPreviewOptions
from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_profiles import UserProfile
from src.databases.likes import Like
from src.databases.user_locations import UserLocation
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb


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
				await event.answer("❌ کاربر یافت نشد.", reply_markup=kb)
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
			# Build caption
			caption_lines = [
				f"• نام: {name}",
				f"• جنسیت: {gender_text}",
				f"• استان: {state_name}",
				f"• شهر: {city_name}",
				f"• سن: {age}",
				"",
				f"🆔 آیدی : /user_{unique_id}",
				"",
				f"🏁 فاصله از شما:  {distance_str}",
			]
			caption = "\n".join(caption_lines)
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
			from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
			from src.databases.user_blocked import UserBlocked
			from src.databases.contacts import Contact
			# likes count already fetched, liked state computed
			rows = []
			rows.append([InlineKeyboardButton(text=f"{like_emoji} {likes_count}", callback_data=f"profile_like:{unique_id}")])
			rows.append([
				InlineKeyboardButton(text="درخواست چت", callback_data=f"profile_chat_request:{unique_id}"),
				InlineKeyboardButton(text="پیام دایرکت", callback_data=f"profile_direct:{unique_id}"),
			])
			# Block/unblock
			is_blocked = False
			if me:
				is_blocked = bool(await session.scalar(select(func.count(UserBlocked.id)).where(UserBlocked.user_id == me.id, UserBlocked.target_id == target.id)))
			block_text = "آن‌بلاک کردن کاربر" if is_blocked else "بلاک کردن کاربر"
			rows.append([InlineKeyboardButton(text=block_text, callback_data=f"profile_block_toggle:{unique_id}")])
			# Contacts add/remove
			in_contacts = False
			if me:
				in_contacts = bool(await session.scalar(select(func.count(Contact.id)).where(Contact.user_id == me.id, Contact.target_id == target.id)))
			contacts_text = "حذف از مخاطبین" if in_contacts else "افزودن به مخاطبین"
			rows.append([InlineKeyboardButton(text=contacts_text, callback_data=f"profile_contact_toggle:{unique_id}")])
			kb_inline = InlineKeyboardMarkup(inline_keyboard=rows)
			# Send
			file = FSInputFile(photo_path)
			await event.answer_photo(file, caption=caption, reply_markup=kb_inline)
			return None
		# Fallback to next
		return await handler(event, data)


