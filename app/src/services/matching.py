import asyncio
from typing import Optional

from sqlalchemy import select

from src.core.database import get_session
from src.databases.chat_queue import ChatQueue
from src.databases.chats import Chat
from src.databases.users import User


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	# Earth radius in KM
	from math import radians, sin, cos, atan2, sqrt
	r = 6371.0
	phi1 = radians(lat1)
	phi2 = radians(lat2)
	dphi = radians(lat2 - lat1)
	dlam = radians(lon2 - lon1)
	a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	return r * c


def _age_ok(q: ChatQueue, other: ChatQueue) -> bool:
	if q.filter_age_range_from is not None and (other.user_age is None or int(other.user_age) < int(q.filter_age_range_from)):
		return False
	if q.filter_age_range_until is not None and (other.user_age is None or int(other.user_age) > int(q.filter_age_range_until)):
		return False
	return True


def _gender_ok(q: ChatQueue, other: ChatQueue) -> bool:
	# Only enforce when True. False means no filter in this app's semantics.
	if bool(q.filter_only_boy):
		return bool(other.user_is_boy)
	if bool(q.filter_only_girl):
		return bool(other.user_is_girl)
	return True


def _state_city_ok(q: ChatQueue, other: ChatQueue) -> bool:
	if bool(q.filter_only_state):
		if q.user_state_id is None or other.user_state_id is None:
			return False
		if int(q.user_state_id) != int(other.user_state_id):
			return False
	if bool(q.filter_only_city):
		if q.user_city_id is None or other.user_city_id is None:
			return False
		if int(q.user_city_id) != int(other.user_city_id):
			return False
	return True


def _distance_ok(q: ChatQueue, other: ChatQueue) -> bool:
	if q.filter_location_distance is None:
		return True
	if q.user_location_x is None or q.user_location_y is None:
		return False
	if other.user_location_x is None or other.user_location_y is None:
		return False
	d = _haversine_km(float(q.user_location_x), float(q.user_location_y), float(other.user_location_x), float(other.user_location_y))
	return d <= float(q.filter_location_distance)


def _mutual_ok(a: ChatQueue, b: ChatQueue) -> bool:
	return (
		_age_ok(a, b)
		and _gender_ok(a, b)
		and _state_city_ok(a, b)
		and _distance_ok(a, b)
		and _age_ok(b, a)
		and _gender_ok(b, a)
		and _state_city_ok(b, a)
		and _distance_ok(b, a)
	)


async def process_one_match(bot) -> bool:
	"""
	Try to match the oldest queue row. Returns True if a match was made.
	"""
	async with get_session() as session:
		first: ChatQueue | None = await session.scalar(select(ChatQueue).order_by(ChatQueue.id.asc()))
		if not first:
			return False
		# Load requester user and ensure still searching
		req_user: User | None = await session.scalar(select(User).where(User.id == first.user_id))
		if not req_user or req_user.step != "searching":
			# Drop stale queue
			await session.delete(first)
			await session.commit()
			return False
		# Find candidates (oldest first, excluding self)
		cand_rows = list(await session.scalars(select(ChatQueue).where(ChatQueue.user_id != first.user_id).order_by(ChatQueue.id.asc())))
		chosen: Optional[ChatQueue] = None
		for cand in cand_rows:
			cand_user: User | None = await session.scalar(select(User).where(User.id == cand.user_id))
			if not cand_user or cand_user.step != "searching":
				continue
			if _mutual_ok(first, cand):
				chosen = cand
				break
		if not chosen:
			# Nothing to do this tick
			return False
		# Create chat, update steps, remove queues
		chat = Chat(user1_id=first.user_id, user2_id=chosen.user_id)
		session.add(chat)
		req_user.step = "chatting"
		cand_user2: User | None = await session.scalar(select(User).where(User.id == chosen.user_id))
		if cand_user2:
			cand_user2.step = "chatting"
		await session.flush()
		await session.delete(first)
		await session.delete(chosen)
		await session.commit()
		# Notify both users
		from src.context.keyboards.reply.chat_actions import build_keyboard as build_chat_kb
		message_text = (
			"👀 پیدا کردم و وصل‌تون کردم!\n"
			"به مخاطبت سلام کن 🗣️\n\n"
			"⚠️ هشدار جدی!:\n"
			"اگر مخاطبی که وصل شدید، در همان ابتدای چت درخواست پیوی داد (برای آشنایی و...)، این فرد  فیک و کلاهبرداره.\n"
			"لطفاً سریعاً گزارش دهید و به هیچ وجه اعتماد نکنید!!!."
		)
		kb, _ = build_chat_kb()
		# Resolve Telegram ids
		u1: User | None = await session.scalar(select(User).where(User.id == chat.user1_id))
		u2: User | None = await session.scalar(select(User).where(User.id == chat.user2_id))
		for u in (u1, u2):
			if u and u.user_id:
				try:
					await bot.send_message(int(u.user_id), message_text, reply_markup=kb)
				except Exception:
					pass
		return True


async def run_matching_loop(bot) -> None:
	while True:
		try:
			made = await process_one_match(bot)
			# If a match was made, try to continue quickly to reduce queue; else sleep 5s
			await asyncio.sleep(0 if made else 5)
		except Exception:
			# Never crash the loop
			await asyncio.sleep(5)



