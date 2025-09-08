from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy import select, delete

from src.core.database import get_session
from src.databases.users import User
from src.databases.likes import Like
from src.databases.user_blocked import UserBlocked
from src.databases.contacts import Contact
from src.databases.user_profiles import UserProfile
from src.databases.user_locations import UserLocation
from src.context.messages.visitor.profile_view import format_caption
from src.context.keyboards.inline.visitor_profile import build_keyboard as build_visitor_kb
from src.services.user_activity import get_last_activity_string


async def _render_profile(callback: CallbackQuery, target: User) -> None:
	from sqlalchemy import func
	async with get_session() as session:
		profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == target.id))
		likes_count = int((await session.scalar(select(func.count(Like.id)).where(Like.target_id == target.id))) or 0)
		# Resolve viewer and states
		viewer_id = callback.from_user.id if callback.from_user else 0
		viewer: User | None = await session.scalar(select(User).where(User.user_id == viewer_id))
		# Like state
		liked = False
		if viewer:
			liked = bool(await session.scalar(select(func.count(Like.id)).where(Like.user_id == viewer.id, Like.target_id == target.id)))
		# Block/contact states
		is_blocked = False
		in_contacts = False
		if viewer:
			is_blocked = bool(await session.scalar(select(func.count(UserBlocked.id)).where(UserBlocked.user_id == viewer.id, UserBlocked.target_id == target.id)))
			in_contacts = bool(await session.scalar(select(func.count(Contact.id)).where(Contact.user_id == viewer.id, Contact.target_id == target.id)))
		# Names
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
		# Distance
		distance_str = "نامشخص"
		try:
			from src.services.nearby_search import _haversine_km  # type: ignore
		except Exception:
			_haversine_km = None  # type: ignore
		if viewer:
			me_loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == viewer.id))
			t_loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == target.id))
			if _haversine_km and me_loc and t_loc and me_loc.location_x is not None and t_loc.location_x is not None:
				d = _haversine_km(me_loc.location_x, me_loc.location_y, t_loc.location_x, t_loc.location_y)
				distance_str = f"{int(round(d))}KM"
		# Photo path
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
		# Render
		last_activity_status = await get_last_activity_string(target.id)
		caption = format_caption(
			name=name,
			gender_text=gender_text,
			state_name=state_name,
			city_name=city_name,
			age=age,
			unique_id=target.unique_id or str(target.id),
			distance_text=distance_str,
			last_activity=last_activity_status,
		)
		kb_inline = build_visitor_kb(
			unique_id=target.unique_id or str(target.id),
			liked=liked,
			likes_count=likes_count,
			is_blocked=is_blocked,
			in_contacts=in_contacts,
		)
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer_photo(FSInputFile(photo_path), caption=caption, reply_markup=kb_inline)
		await callback.answer()


async def handle_visitor_profile_action(callback: CallbackQuery) -> None:
	data = callback.data or ""
	viewer_tg_id = callback.from_user.id if callback.from_user else 0
	cmd, _, unique_id = data.partition(":")
	async with get_session() as session:
		target: User | None = await session.scalar(select(User).where(User.unique_id == unique_id))
		viewer: User | None = await session.scalar(select(User).where(User.user_id == viewer_tg_id))
		if not target or not viewer:
			await callback.answer()
			return
		if cmd == "profile_like":
			# Toggle like
			exists = await session.scalar(select(Like.id).where(Like.user_id == viewer.id, Like.target_id == target.id))
			if exists:
				await session.execute(delete(Like).where(Like.id == exists))
				await session.commit()
			else:
				like = Like(user_id=viewer.id, target_id=target.id)
				session.add(like)
				await session.commit()
		elif cmd == "profile_block_toggle":
			row_id = await session.scalar(select(UserBlocked.id).where(UserBlocked.user_id == viewer.id, UserBlocked.target_id == target.id))
			if row_id:
				await session.execute(delete(UserBlocked).where(UserBlocked.id == row_id))
				await session.commit()
			else:
				row = UserBlocked(user_id=viewer.id, target_id=target.id)
				session.add(row)
				await session.commit()
		elif cmd == "profile_contact_toggle":
			row_id = await session.scalar(select(Contact.id).where(Contact.user_id == viewer.id, Contact.target_id == target.id))
			if row_id:
				await session.execute(delete(Contact).where(Contact.id == row_id))
				await session.commit()
			else:
				row = Contact(user_id=viewer.id, target_id=target.id)
				session.add(row)
				await session.commit()
		# Re-render updated profile view
	await _render_profile(callback, target)


