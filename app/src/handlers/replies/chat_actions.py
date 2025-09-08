from aiogram.types import Message
from sqlalchemy import select, or_, func

from src.core.database import get_session
from src.databases.users import User
from src.databases.chats import Chat
from src.context.messages.chat.end_confirm import get_message as get_end_confirm
from src.context.keyboards.inline.chat_end_confirm import build_keyboard as build_confirm_kb
from src.context.keyboards.reply.chat_actions import resolve_id_from_text
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb, build_keyboard_for
from src.databases.user_profiles import UserProfile
from src.databases.user_locations import UserLocation
from src.databases.likes import Like
from src.databases.user_blocked import UserBlocked
from src.databases.contacts import Contact
from src.databases.states import State
from src.databases.cities import City
from src.context.messages.visitor.profile_view import format_caption as visitor_format_caption
from src.context.keyboards.inline.visitor_profile import build_keyboard as build_visitor_kb
from src.services.user_activity import get_last_activity_string
from pathlib import Path


async def handle_chat_action(message: Message) -> None:
	text = message.text or ""
	action = resolve_id_from_text(text)
	if action is None:
		return
	if action == "chat:partner_profile":
		# Show partner profile directly (same as visitor middleware rendering)
		user_tg_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
			if not me:
				return
			chat: Chat | None = await session.scalar(
				select(Chat).where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id)).order_by(Chat.id.desc())
			)
			if not chat:
				return
			partner_id = chat.user2_id if chat.user1_id == me.id else chat.user1_id
			partner: User | None = await session.scalar(select(User).where(User.id == partner_id))
			if not partner:
				return
			profile: UserProfile | None = await session.scalar(select(UserProfile).where(UserProfile.user_id == partner.id))
			# Likes
			likes_count = int((await session.scalar(select(func.count(Like.id)).where(Like.target_id == partner.id))) or 0)
			liked = bool(await session.scalar(select(func.count(Like.id)).where(Like.user_id == me.id, Like.target_id == partner.id)))
			# Block/contacts
			is_blocked = bool(await session.scalar(select(func.count(UserBlocked.id)).where(UserBlocked.user_id == me.id, UserBlocked.target_id == partner.id)))
			in_contacts = bool(await session.scalar(select(func.count(Contact.id)).where(Contact.user_id == me.id, Contact.target_id == partner.id)))
			# Names and location
			name = (profile.name if profile and profile.name else None) or (partner.tg_name or "بدون نام")
			age = str(profile.age) if profile and profile.age is not None else "?"
			gender_text = "دختر" if (profile and profile.is_female) else ("پسر" if (profile and profile and profile.is_female is not None) else "نامشخص")
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
			# Distance (optional)
			distance_str = "نامشخص"
			me_loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == me.id))
			t_loc: UserLocation | None = await session.scalar(select(UserLocation).where(UserLocation.user_id == partner.id))
			try:
				from src.services.nearby_search import _haversine_km  # type: ignore
			except Exception:
				_haversine_km = None  # type: ignore
			if _haversine_km and me_loc and t_loc and me_loc.location_x is not None and t_loc.location_x is not None:
				d = _haversine_km(me_loc.location_x, me_loc.location_y, t_loc.location_x, t_loc.location_y)
				distance_str = f"{int(round(d))}KM"
			# Photo path resolve (custom avatar or default by gender)
			photo_path = None
			avatars_dir = Path("src") / "storage" / "avatars"
			candidates = [avatars_dir / f"{partner.id}.jpg", avatars_dir / f"{partner.id}.jpeg", avatars_dir / f"{partner.id}.png"]
			for p in candidates:
				if p.exists():
					photo_path = str(p.resolve())
					break
			if not photo_path:
				photo_path = "src/context/resources/images/noimage-girl.jpg" if (profile and profile.is_female) else "src/context/resources/images/noimage-boy.jpg"
			last_activity_status = await get_last_activity_string(partner.id)
			caption = visitor_format_caption(
				name=name,
				gender_text=gender_text,
				state_name=state_name,
				city_name=city_name,
				age=age,
				unique_id=partner.unique_id or str(partner.id),
				distance_text=distance_str,
				last_activity=last_activity_status,
			)
			kb_inline = build_visitor_kb(
				unique_id=partner.unique_id or str(partner.id),
				liked=liked,
				likes_count=likes_count,
				is_blocked=is_blocked,
				in_contacts=in_contacts,
			)
			from aiogram.types import FSInputFile
			await message.answer_photo(FSInputFile(photo_path), caption=caption, reply_markup=kb_inline)
		return
	if action == "chat:delete_messages":
		user_tg_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
			if not me:
				return
			chat: Chat | None = await session.scalar(
				select(Chat).where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id)).order_by(Chat.id.desc())
			)
			if not chat:
				return
		from src.context.messages.chat.delete_messages_hint import format_message as get_del_hint
		await message.answer(get_del_hint(chat.id))
		return
	if action == "chat:secure_toggle":
		user_tg_id = message.from_user.id if message.from_user else 0
		async with get_session() as session:
			me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
			if not me:
				return
			chat: Chat | None = await session.scalar(
				select(Chat).where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id)).order_by(Chat.id.desc())
			)
			if not chat:
				return
			# Toggle secure_chat
			new_status = not bool(chat.secure_chat)
			chat.secure_chat = new_status
			await session.commit()
			# Notify both sides
			from src.context.messages.chat.secure_chat_status import format_message as get_secure_msg
			try:
				await message.answer(get_secure_msg(new_status))
			except Exception:
				pass
			# Partner
			partner_id = chat.user2_id if chat.user1_id == me.id else chat.user1_id
			partner: User | None = await session.scalar(select(User).where(User.id == partner_id))
			if partner and partner.user_id:
				try:
					await message.bot.send_message(int(partner.user_id), get_secure_msg(new_status))
				except Exception:
					pass
		return
	if action != "chat:end":
		return
	user_tg_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		me: User | None = await session.scalar(select(User).where(User.user_id == user_tg_id))
		if not me:
			return
		chat: Chat | None = await session.scalar(
			select(Chat).where(or_(Chat.user1_id == me.id, Chat.user2_id == me.id)).order_by(Chat.id.desc())
		)
		if not chat:
			return
	await message.answer(get_end_confirm(), reply_markup=build_confirm_kb(chat.id))


