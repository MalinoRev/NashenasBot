from typing import Any, Callable, Dict, Optional, List
import re

from aiogram import BaseMiddleware
from aiogram.types import (
	CallbackQuery,
	KeyboardButton,
	Message,
	ReplyKeyboardMarkup,
	ReplyKeyboardRemove,
    LinkPreviewOptions,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.databases.user_profiles import UserProfile
from src.context.messages.profileMiddleware.enterName import get_message as get_enter_name_message
from src.context.messages.profileMiddleware.invalidName import get_message as get_invalid_name_message
from src.context.messages.profileMiddleware.invalidNameNonPersian import get_message as get_invalid_name_non_persian_message
from src.context.messages.profileMiddleware.chooseGender import get_message as get_choose_gender_message
from src.context.messages.profileMiddleware.invalidGender import get_message as get_invalid_gender_message
from src.context.messages.profileMiddleware.chooseAge import get_message as get_choose_age_message
from src.context.messages.profileMiddleware.invalidAge import get_message as get_invalid_age_message
from src.context.messages.profileMiddleware.invalidAgeRange import get_message as get_invalid_age_range_message
from src.context.messages.profileMiddleware.chooseState import get_message as get_choose_state_message
from src.context.messages.profileMiddleware.invalidState import get_message as get_invalid_state_message
from src.context.messages.profileMiddleware.chooseCity import get_message as get_choose_city_message
from src.context.messages.profileMiddleware.profileCompleted import get_message as get_profile_completed_message
from src.context.messages.profileMiddleware.invalidCommand import get_message as get_invalid_command_message
from src.context.messages.profileMiddleware.nameUpdated import get_message as get_name_updated_message
from src.context.messages.profileMiddleware.genderUpdated import get_message as get_gender_updated_message
from src.context.messages.profileMiddleware.ageUpdated import get_message as get_age_updated_message
from src.context.messages.profileMiddleware.stateCityUpdated import get_message as get_state_city_updated_message
from src.context.keyboards.reply.gender import build_keyboard as build_gender_kb, resolve_id_from_text as resolve_gender_id
from src.context.keyboards.reply.age import build_keyboard as build_age_kb, resolve_id_from_text as resolve_age_id
from src.context.keyboards.reply.state import build_keyboard as build_state_kb, resolve_id_from_text as resolve_state_id
from src.context.keyboards.reply.city import build_keyboard as build_city_kb, resolve_id_from_text as resolve_city_id
from src.context.keyboards.reply.mainButtons import build_keyboard as build_main_kb, build_keyboard_for
from src.context.messages.commands.start import get_message as get_start_message
from src.databases.users import User
from src.databases.states import State
from src.databases.cities import City


def _normalize_digits(text: str) -> str:
	# Convert Persian and Arabic-Indic digits to ASCII
	translate_map = str.maketrans({
		"۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
		"۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
		"٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
		"٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
	})
	return text.translate(translate_map)


class ProfileMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# Must run after AuthMiddleware
		if not data.get("auth_ok"):
			return None

		user_id: Optional[int] = None
		if isinstance(event, Message):
			if event.from_user:
				user_id = event.from_user.id
		elif isinstance(event, CallbackQuery):
			if event.from_user:
				user_id = event.from_user.id

		if not user_id:
			data["profile_ok"] = False
			return None

		# Interactive profile completion flow (messages only)
		if isinstance(event, CallbackQuery):
			# Skip profile prompts on callbacks; let handlers manage
			data["profile_ok"] = True
			return await handler(event, data)

		text = (event.text or "").strip()
		async with get_session() as session:
			# user_id here is Telegram user id. Fetch DB user and use its primary key for profile FK
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if user is None:
				# Should not happen if AuthMiddleware ran, but guard anyway
				data["profile_ok"] = False
				return None

			profile: UserProfile | None = await session.scalar(
				select(UserProfile).where(UserProfile.user_id == user.id)
			)

			# Direct message flow intercept: if user.step like direct_to_{targetId}, show confirm UI and on confirm send
			if getattr(user, "step", "").startswith("direct_to_"):
				# Parse target id
				try:
					target_id_str = user.step.split("direct_to_", 1)[1]
					target_internal_id = int(target_id_str)
				except Exception:
					target_internal_id = None
				if target_internal_id is not None:
					# If user pressed back, cancel and show /start
					from src.context.keyboards.reply.special_contact import resolve_id_from_text as _resolve_special_back
					if _resolve_special_back(text) == "special:back":
						user.step = "start"
						await session.commit()
						name_display = None
						if isinstance(event, Message) and event.from_user:
							name_display = event.from_user.first_name or event.from_user.username
						start_text = get_start_message(name_display)
						kb0, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
						await event.answer(
							start_text,
							reply_markup=kb0,
							parse_mode="Markdown",
							link_preview_options=LinkPreviewOptions(is_disabled=True),
						)
						return None
					# Save draft and show confirm UI replying to user's message
					from src.services.direct_draft_cache import set_draft, MessageData
					from src.context.keyboards.inline.direct_send_confirm import build_keyboard as _build_confirm_kb
					from src.context.messages.direct.confirm_preview import format_message as _confirm_text
					from src.databases.users import User as _U2
					target_user: _U2 | None = await session.scalar(select(_U2).where(_U2.id == target_internal_id))
					target_uid = target_user.unique_id if target_user and target_user.unique_id else str(target_internal_id)

					# Create MessageData object with message content
					message_data = MessageData(
						text=event.text,
						photo=event.photo,
						video=event.video,
						animation=event.animation,
						audio=event.audio,
						document=event.document,
						sticker=event.sticker,
						caption=event.caption
					)

					set_draft(user.id, event.chat.id, event.message_id, target_internal_id, message_data)
					# Reply to user's own message with confirm note
					await event.bot.send_message(
						chat_id=event.chat.id,
						text=_confirm_text(target_uid),
						reply_to_message_id=event.message_id,
						reply_markup=_build_confirm_kb(target_uid),
					)
					# Do not consume credit now; wait for confirm
					return None

			# Direct list message flow intercept: if user.step like direct_list_to_{id-id-...}, collect message for list sending
			if getattr(user, "step", "").startswith("direct_list_"):
				# Parse step to get kind and page (kind may contain underscores)
				kind = None
				page = None
				recipients_ids: list[int] = []
				try:
					rest = user.step[len("direct_list_"):]
					if rest.startswith("to_"):
						ids_str = rest[len("to_"):]
						recipients_ids = [int(x) for x in ids_str.split("-") if x.isdigit()]
					else:
						# legacy pattern direct_list_{kind}_{page}
						kind, page_str = rest.rsplit("_", 1)
						page = int(page_str)
				except Exception:
					pass
				
				if recipients_ids or (kind is not None and page is not None):
					# If user pressed back, cancel and show /start
					from src.context.keyboards.reply.special_contact import resolve_id_from_text as _resolve_special_back
					if _resolve_special_back(text) == "special:back":
						user.step = "start"
						await session.commit()
						name_display = None
						if isinstance(event, Message) and event.from_user:
							name_display = event.from_user.first_name or event.from_user.username
						start_text = get_start_message(name_display)
						kb0, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
						await event.answer(
							start_text,
							reply_markup=kb0,
							parse_mode="Markdown",
							link_preview_options=LinkPreviewOptions(is_disabled=True),
						)
						return None
					
					# Create MessageData from current message exactly like single direct
					from src.services.direct_draft_cache import MessageData as _Msg
					message_data = _Msg(
						text=event.text,
						photo=event.photo,
						video=event.video,
						animation=event.animation,
						audio=event.audio,
						document=event.document,
						sticker=event.sticker,
						caption=event.caption,
					)
					# Build JSON content identical to single direct flow, will be replicated per recipient in next phase
					json_message_data = {}
					if message_data.text:
						json_message_data = {"message": message_data.text, "type": "text"}
					elif message_data.photo:
						# Save media to cache channel (if configured) to obtain media_id
						from src.services.cache import CacheService
						cache_service = CacheService(event.bot)
						media_id = await cache_service.save_media(message_data.photo[-1])
						json_message_data = {"message": message_data.caption or "", "type": "image", "media_id": media_id}
					elif message_data.video:
						from src.services.cache import CacheService
						cache_service = CacheService(event.bot)
						media_id = await cache_service.save_media(message_data.video)
						json_message_data = {"message": message_data.caption or "", "type": "video", "media_id": media_id}
					elif message_data.animation:
						from src.services.cache import CacheService
						cache_service = CacheService(event.bot)
						media_id = await cache_service.save_media(message_data.animation)
						json_message_data = {"message": message_data.caption or "", "type": "animation", "media_id": media_id}
					elif message_data.audio:
						from src.services.cache import CacheService
						cache_service = CacheService(event.bot)
						media_id = await cache_service.save_media(message_data.audio)
						json_message_data = {"message": message_data.caption or "", "type": "audio", "media_id": media_id}
					elif message_data.document:
						from src.services.cache import CacheService
						cache_service = CacheService(event.bot)
						media_id = await cache_service.save_media(message_data.document)
						json_message_data = {"message": message_data.caption or "", "type": "document", "media_id": media_id}
					elif message_data.sticker:
						from src.services.cache import CacheService
						cache_service = CacheService(event.bot)
						media_id = await cache_service.save_media(message_data.sticker)
						json_message_data = {"message": "", "type": "sticker", "media_id": media_id}
					else:
						await event.answer("❌ نوع پیام پشتیبانی نمی‌شود", show_alert=True)
						return None
					# Save the direct as a list draft entry per-user (temporary target_id = sender for now)
					from src.databases.directs import Direct
					from sqlalchemy import insert
					if recipients_ids:
						# Save one row per recipient id
						for rid in recipients_ids:
							await session.execute(insert(Direct).values(user_id=user.id, target_id=rid, content=json_message_data))
					else:
						# Fallback: store as self to be handled later (should not happen with new flow)
						await session.execute(insert(Direct).values(user_id=user.id, target_id=user.id, content=json_message_data))
					# Keep step with stabilized recipient ids until user confirms/cancels
					await session.commit()
					# Send list confirmation preview with confirm/cancel/edit keyboard
					from src.context.messages.direct.list_confirm_preview import format_header as _list_header, format_footer as _list_footer
					from src.context.keyboards.inline.direct_list_send_confirm import build_keyboard as _list_kb
					try:
						# Header
						preview_text = _list_header()
						if recipients_ids:
							from sqlalchemy import select as _select2, func as _func2
							from src.databases.users import User as _U3
							from src.databases.user_profiles import UserProfile as _UP3
							from src.databases.likes import Like as _Like3
							import html as _html
							res = await session.execute(
								_select2(_U3, _UP3).join(_UP3, _UP3.user_id == _U3.id, isouter=True).where(_U3.id.in_(recipients_ids))
							)
							rows_map = {u.id: (u, p) for (u, p) in res.all()
							}
							if recipients_ids:
								likes_res = await session.execute(
									_select2(_Like3.target_id, _func2.count(_Like3.id)).where(_Like3.target_id.in_(recipients_ids)).group_by(_Like3.target_id)
								)
								likes_counts = dict(likes_res.all())
							else:
								likes_counts = {}
							lines: list[str] = []
							for rid in recipients_ids:
								u, p = rows_map.get(rid, (None, None))
								if not u:
									continue
								name = (p.name if p and p.name else None) or (u.tg_name or "بدون نام")
								age = p.age if p and p.age is not None else "?"
								if p and p.is_female is True:
									emoji = "👩"
									gender_word = "دختر"
								elif p and p.is_female is False:
									emoji = "👨"
									gender_word = "پسر"
								else:
									emoji = "❔"
									gender_word = "نامشخص"
								likes = likes_counts.get(rid, 0)
								unique_id = u.unique_id or str(u.id)
								block_inner = (
									f"🔸 کاربر {_html.escape(str(name))} | {emoji} {gender_word} | سن: {_html.escape(str(age))} | {_html.escape(str(likes))} ❤️\n"
									f"👤 پروفایل: /user_{_html.escape(str(unique_id))}"
								)
								lines.append(f"<blockquote>{block_inner}</blockquote>")
							if lines:
								preview_text = preview_text + "\n\n" + "\n".join(lines)
						# Footer with cost and balance
						cost = len(recipients_ids)
						balance = int(user.credit or 0)
						preview_text = preview_text + _list_footer(cost, balance)
						await event.answer(preview_text, parse_mode="HTML", reply_markup=_list_kb("list", 1))
					except Exception:
						await event.answer(_list_header(), reply_markup=_list_kb("list", 1))
					return None

			# If a command is sent while profile is not complete, block it
			if text.startswith("/"):
				incomplete = (
					profile is None
					or profile.name is None
					or profile.is_female is None
					or profile.age is None
					or profile.state is None
					or profile.city is None
				)
				if incomplete:
					# Special case: if profile does not exist yet, start the flow without sending invalid-command
					if profile is None:
						profile = UserProfile(user_id=user.id)
						session.add(profile)
						user.step = "ask_name"
						await session.commit()
						await event.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
						return None
					await event.answer(get_invalid_command_message(), reply_markup=ReplyKeyboardRemove())
					# Re-send the expected prompt for the current step
					if getattr(user, "step", "start") == "edit_name":
						await event.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
						return None
					if getattr(user, "step", "start") == "ask_name" or profile.name is None:
						await event.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
						return None
					elif getattr(user, "step", "start") in {"ask_gender", "edit_gender"} or profile.is_female is None:
						gender_kb, _ = build_gender_kb()
						await event.answer(get_choose_gender_message(), reply_markup=gender_kb)
						return None
					elif getattr(user, "step", "start") in {"ask_age", "edit_age"} or profile.age is None:
						age_kb, _ = build_age_kb()
						await event.answer(get_choose_age_message(), reply_markup=age_kb)
						return None
					elif getattr(user, "step", "start") in {"ask_state", "edit_state"} or profile.state is None:
						states: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
						if states:
							state_kb, _ = build_state_kb([s.state_name for s in states])
							await event.answer(get_choose_state_message(), reply_markup=state_kb)
							return None
					elif getattr(user, "step", "start") in {"ask_city", "edit_city"} or profile.city is None:
						state_id = profile.state
						if state_id:
							cities: List[City] = list(
								await session.scalars(
									select(City).where(City.state_id == state_id).order_by(City.city_name)
								)
							)
							if cities:
								city_kb, _ = build_city_kb([c.city_name for c in cities])
								await event.answer(get_choose_city_message(), reply_markup=city_kb)
								return None
						# Fallback: if state not set yet, re-ask state
						await event.answer(get_choose_state_message(), reply_markup=ReplyKeyboardRemove())
						return None
			if profile is None:
				profile = UserProfile(user_id=user.id)
				session.add(profile)
				user.step = "ask_name"
				await session.commit()
				await event.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
				return None

			# Edit flow: change name when step is 'edit_name'
			if getattr(user, "step", "start") == "edit_name":
				if not text:
					await event.answer(get_invalid_name_message(), reply_markup=ReplyKeyboardRemove())
					return None
				persian_name_pattern = r"^[\u0600-\u06FF\u200c\s]+$"
				if not re.match(persian_name_pattern, text):
					await event.answer(get_invalid_name_non_persian_message(), reply_markup=ReplyKeyboardRemove())
					return None
				profile.name = text
				user.step = "start"
				await session.commit()
				await event.answer(get_name_updated_message(), reply_markup=ReplyKeyboardRemove())
				# Also send /start exactly as elsewhere
				name_display = None
				if isinstance(event, Message) and event.from_user:
					name_display = event.from_user.first_name or event.from_user.username
				start_text = get_start_message(name_display)
				kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
				await event.answer(
					start_text,
					reply_markup=kb,
					parse_mode="Markdown",
					link_preview_options=LinkPreviewOptions(is_disabled=True),
				)
				data["profile_ok"] = False
				return None

			# Step 1: name
			if profile.name is None:
				if user.step != "ask_name":
					user.step = "ask_name"
					await session.commit()
					await event.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
					return None
				if not text:
					await event.answer(get_invalid_name_message(), reply_markup=ReplyKeyboardRemove())
					return None
				# Validate Persian-only letters (allow spaces and ZWNJ)
				persian_name_pattern = r"^[\u0600-\u06FF\u200c\s]+$"
				if not re.match(persian_name_pattern, text):
					await event.answer(get_invalid_name_non_persian_message(), reply_markup=ReplyKeyboardRemove())
					return None
				profile.name = text
				user.step = "ask_gender"
				await session.commit()
				gender_kb, _ = build_gender_kb()
				await event.answer(get_choose_gender_message(), reply_markup=gender_kb)
				return None

			# Step 2: gender (and edit flow)
			if profile.is_female is None or getattr(user, "step", "start") == "edit_gender":
				if user.step not in {"ask_gender", "edit_gender"}:
					user.step = "ask_gender"
					await session.commit()
					gender_kb, _ = build_gender_kb()
					await event.answer(get_choose_gender_message(), reply_markup=gender_kb)
					return None
				normalized = text.lower()
				# Prefer matching via stable ids when possible
				gender_id = resolve_gender_id(text)
				if gender_id == "gender:female" or normalized in {"زن", "زنانه", "female", "f"}:
					profile.is_female = True
				elif gender_id == "gender:male" or normalized in {"مرد", "آقا", "male", "m"}:
					profile.is_female = False
				else:
					gender_kb, _ = build_gender_kb()
					await event.answer(get_invalid_gender_message(), reply_markup=gender_kb)
					return None
				# If this was edit flow, finish here with success + start
				if getattr(user, "step", "start") == "edit_gender":
					user.step = "start"
					await session.commit()
					await event.answer(get_gender_updated_message(), reply_markup=ReplyKeyboardRemove())
					# send /start
					name_display = None
					if isinstance(event, Message) and event.from_user:
						name_display = event.from_user.first_name or event.from_user.username
					start_text = get_start_message(name_display)
					kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
					await event.answer(
						start_text,
						reply_markup=kb,
						parse_mode="Markdown",
						link_preview_options=LinkPreviewOptions(is_disabled=True),
					)
					data["profile_ok"] = False
					return None
				# Next: ask age (normal flow)
				user.step = "ask_age"
				await session.commit()
				age_kb, _ = build_age_kb()
				await event.answer(get_choose_age_message(), reply_markup=age_kb)
				return None

			# Step 3: age (and edit flow)
			if profile.age is None or getattr(user, "step", "start") == "edit_age":
				if user.step not in {"ask_age", "edit_age"}:
					user.step = "ask_age"
					await session.commit()
					age_kb, _ = build_age_kb()
					await event.answer(get_choose_age_message(), reply_markup=age_kb)
					return None
				age_id = resolve_age_id(text)
				if age_id is None or not age_id.startswith("age:"):
					# Try parsing free-typed digits (including Persian/Arabic digits)
					normalized = _normalize_digits(text)
					if normalized.isdigit():
						try:
							age_val = int(normalized)
						except Exception:
							age_kb0, _ = build_age_kb()
							await event.answer(get_invalid_age_message(), reply_markup=age_kb0)
							return None
						if age_val < 1 or age_val > 99:
							age_kb1, _ = build_age_kb()
							await event.answer(get_invalid_age_range_message(), reply_markup=age_kb1)
							return None
						profile.age = age_val
						# If this was edit flow, finish with success + start
						if getattr(user, "step", "start") == "edit_age":
							user.step = "start"
							await session.commit()
							await event.answer(get_age_updated_message(), reply_markup=ReplyKeyboardRemove())
							# send /start
							name_display = None
							if isinstance(event, Message) and event.from_user:
								name_display = event.from_user.first_name or event.from_user.username
							start_text = get_start_message(name_display)
							kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
							await event.answer(
								start_text,
								reply_markup=kb,
								parse_mode="Markdown",
								link_preview_options=LinkPreviewOptions(is_disabled=True),
							)
							data["profile_ok"] = False
							return None
						user.step = "ask_state"
						await session.commit()
						states0: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
						if not states0:
							user.step = "start"
							await session.commit()
							await event.answer(get_profile_completed_message(), reply_markup=ReplyKeyboardRemove())
							data["profile_ok"] = True
							return None
						state_kb0, _ = build_state_kb([s.state_name for s in states0])
						await event.answer(get_choose_state_message(), reply_markup=state_kb0)
						return None
					age_kb, _ = build_age_kb()
					await event.answer(get_invalid_age_message(), reply_markup=age_kb)
					return None
				try:
					age_val = int(age_id.split(":", 1)[1])
				except Exception:
					age_kb2, _ = build_age_kb()
					await event.answer(get_invalid_age_message(), reply_markup=age_kb2)
					return None
				if age_val < 1 or age_val > 99:
					age_kb3, _ = build_age_kb()
					await event.answer(get_invalid_age_range_message(), reply_markup=age_kb3)
					return None
				profile.age = age_val
				# If this was edit flow, finish with success + start
				if getattr(user, "step", "start") == "edit_age":
					user.step = "start"
					await session.commit()
					await event.answer(get_age_updated_message(), reply_markup=ReplyKeyboardRemove())
					name_display = None
					if isinstance(event, Message) and event.from_user:
						name_display = event.from_user.first_name or event.from_user.username
					start_text = get_start_message(name_display)
					kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
					await event.answer(
						start_text,
						reply_markup=kb,
						parse_mode="Markdown",
						link_preview_options=LinkPreviewOptions(is_disabled=True),
					)
					data["profile_ok"] = False
					return None
				# Normal flow: go to state
				user.step = "ask_state"
				await session.commit()
				# Prompt states list
				states: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
				if not states:
					# Gracefully finish profile if no states are configured
					user.step = "start"
					await session.commit()
					await event.answer(get_profile_completed_message(), reply_markup=ReplyKeyboardRemove())
					data["profile_ok"] = True
					return None
				state_kb, _ = build_state_kb([s.state_name for s in states])
				await event.answer(get_choose_state_message(), reply_markup=state_kb)
				return None

			# Step 4: state (and edit flow)
			if profile.state is None or getattr(user, "step", "start") == "edit_state":
				if user.step not in {"ask_state", "edit_state"}:
					user.step = "ask_state"
					await session.commit()
					# Re-show states
					states: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
					state_kb, _ = build_state_kb([s.state_name for s in states])
					await event.answer(get_choose_state_message(), reply_markup=state_kb)
					return None
				# Match state via id mapping
				state_id_candidate = resolve_state_id(text)
				if not state_id_candidate.startswith("state:"):
					states2: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
					state_kb2, _ = build_state_kb([s.state_name for s in states2])
					await event.answer(get_invalid_state_message(), reply_markup=state_kb2)
					return None
				state_name = state_id_candidate.split(":", 1)[1]
				state: State | None = await session.scalar(
					select(State).where(State.state_name == state_name)
				)
				if state is None:
					states3: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
					state_kb3, _ = build_state_kb([s.state_name for s in states3])
					await event.answer(get_invalid_state_message(), reply_markup=state_kb3)
					return None
				profile.state = state.id
				# If editing, proceed to edit city prompt
				if getattr(user, "step", "start") == "edit_state":
					user.step = "edit_city"
				else:
					user.step = "ask_city"
				await session.commit()
				# Prompt cities for the state
				cities: List[City] = list(
					await session.scalars(select(City).where(City.state_id == state.id).order_by(City.city_name))
				)
				if not cities:
					# No cities; finish (if editing, success, else normal finish)
					user.step = "start"
					await session.commit()
					if getattr(user, "step", "start") in {"edit_state", "edit_city"}:
						await event.answer(get_state_city_updated_message(), reply_markup=ReplyKeyboardRemove())
						name_display = None
						if isinstance(event, Message) and event.from_user:
							name_display = event.from_user.first_name or event.from_user.username
						start_text = get_start_message(name_display)
						kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
						await event.answer(
							start_text,
							reply_markup=kb,
							parse_mode="Markdown",
							link_preview_options=LinkPreviewOptions(is_disabled=True),
						)
						data["profile_ok"] = False
						return None
					await event.answer("پروفایل تکمیل شد.", reply_markup=ReplyKeyboardRemove())
					data["profile_ok"] = True
					return await handler(event, data)
				city_kb, _ = build_city_kb([c.city_name for c in cities])
				await event.answer(get_choose_city_message(), reply_markup=city_kb)
				return None

			# Step 4: city (and edit flow)
			if profile.city is None or getattr(user, "step", "start") == "edit_city":
				print(f"LOG: Entered city selection step - user.step: {getattr(user, 'step', 'start')}, profile.city: {profile.city}")
				if user.step not in {"ask_city", "edit_city"}:
					user.step = "ask_city"
					await session.commit()
					await event.answer(get_choose_city_message(), reply_markup=ReplyKeyboardRemove())
					return None
				state_id = profile.state
				if not state_id:
					states4: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
					state_kb4, _ = build_state_kb([s.state_name for s in states4])
					await event.answer("ابتدا استان را انتخاب کنید.", reply_markup=state_kb4)
					return None
				city_id_candidate = resolve_city_id(text)
				if not city_id_candidate.startswith("city:"):
					cities2: List[City] = list(
						await session.scalars(select(City).where(City.state_id == state_id).order_by(City.city_name))
					)
					city_kb2, _ = build_city_kb([c.city_name for c in cities2])
					await event.answer(get_invalid_city_message(), reply_markup=city_kb2)
					return None
				city_name = city_id_candidate.split(":", 1)[1]
				city: City | None = await session.scalar(
					select(City).where(City.state_id == state_id, City.city_name == city_name)
				)
				if city is None:
					cities3: List[City] = list(
						await session.scalars(select(City).where(City.state_id == state_id).order_by(City.city_name))
					)
					city_kb3, _ = build_city_kb([c.city_name for c in cities3])
					await event.answer(get_invalid_city_message(), reply_markup=city_kb3)
					return None
				profile.city = city.id

				# Check if this is first-time completion or edit
				current_step = getattr(user, "step", "start")
				was_edit_flow = current_step == "edit_city"

				print(f"LOG: City selected - current_step: {current_step}, was_edit_flow: {was_edit_flow}")

				user.step = "start"
				await session.commit()

				if was_edit_flow:
					# Edited flow path ends here
					await event.answer(get_state_city_updated_message(), reply_markup=ReplyKeyboardRemove())
					name_display = None
					if isinstance(event, Message) and event.from_user:
						name_display = event.from_user.first_name or event.from_user.username
					start_text = get_start_message(name_display)
					kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
					await event.answer(
						start_text,
						reply_markup=kb,
						parse_mode="Markdown",
						link_preview_options=LinkPreviewOptions(is_disabled=True),
					)
					data["profile_ok"] = False
					return None

				# Normal flow completion (first time profile completion)
				print("LOG: Executing normal flow completion (first time)")
				main_kb, _ = await build_keyboard_for(event.from_user.id if event.from_user else None)
				await event.answer(get_profile_completed_message(), reply_markup=main_kb)

				# Send profile completion info message (only for first-time completion)
				try:
					# Get profile reward amount from database
					from src.databases.rewards import Reward
					reward: Reward | None = await session.scalar(select(Reward))
					profile_reward_amount = int(getattr(reward, "profile_amount", 0)) if reward else 0

					# Get message from context
					from src.context.messages.profileMiddleware.profileCompletionInfo import get_message as get_info_message
					info_message = get_info_message(profile_reward_amount)

					await event.answer(info_message)
					print(f"LOG: Profile completion info message sent to user {user_id} (first time)")

				except Exception as e:
					print(f"LOG: Failed to send profile completion info message: {e}")

				data["profile_ok"] = False
				return None

		# Profile already complete or nothing to do
		# If profile is still incomplete, re-prompt current step instead of delegating to default
		async with get_session() as session2:
			user2: User | None = await session2.scalar(select(User).where(User.user_id == user_id))
			profile2: UserProfile | None = None
			if user2 is not None:
				profile2 = await session2.scalar(select(UserProfile).where(UserProfile.user_id == user2.id))
			if user2 is not None and profile2 is not None:
				if profile2.name is None:
					await event.answer(get_enter_name_message(), reply_markup=ReplyKeyboardRemove())
					return None
				if profile2.is_female is None:
					gender_kb, _ = build_gender_kb()
					await event.answer(get_choose_gender_message(), reply_markup=gender_kb)
					return None
				if profile2.age is None:
					age_kb, _ = build_age_kb()
					await event.answer(get_choose_age_message(), reply_markup=age_kb)
					return None
				if profile2.state is None:
					states: List[State] = list(await session2.scalars(select(State).order_by(State.state_name)))
					if states:
						state_kb, _ = build_state_kb([s.state_name for s in states])
						await event.answer(get_choose_state_message(), reply_markup=state_kb)
						return None
				if profile2.city is None:
					if profile2.state:
						cities: List[City] = list(
							await session2.scalars(select(City).where(City.state_id == profile2.state).order_by(City.city_name))
						)
						city_kb, _ = build_city_kb([c.city_name for c in cities])
						await event.answer(get_choose_city_message(), reply_markup=city_kb)
						return None
					states_fallback: List[State] = list(await session2.scalars(select(State).order_by(State.state_name)))
					state_kb_fb, _ = build_state_kb([s.state_name for s in states_fallback])
					await event.answer(get_choose_state_message(), reply_markup=state_kb_fb)
					return None

		data["profile_ok"] = True
		return await handler(event, data)


