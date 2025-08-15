from typing import Any, Callable, Dict, Optional, List

from aiogram import BaseMiddleware
from aiogram.types import (
	CallbackQuery,
	KeyboardButton,
	Message,
	ReplyKeyboardMarkup,
	ReplyKeyboardRemove,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database import get_session
from src.databases.user_profiles import UserProfile
from src.databases.users import User
from src.databases.states import State
from src.databases.cities import City


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

		# Interactive profile completion flo
  # w (messages only)
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
			if profile is None:
				profile = UserProfile(user_id=user.id)
				session.add(profile)
				user.step = "ask_name"
				await session.commit()
				await event.answer("لطفاً نام خود را وارد کنید:")
				return None

			# Step 1: name
			if profile.name is None:
				if user.step != "ask_name":
					user.step = "ask_name"
					await session.commit()
					await event.answer("لطفاً نام خود را وارد کنید:")
					return None
				if not text:
					await event.answer("نام معتبر وارد کنید:")
					return None
				profile.name = text
				user.step = "ask_gender"
				await session.commit()
				keyboard = ReplyKeyboardMarkup(
					keyboard=[[KeyboardButton(text="زن"), KeyboardButton(text="مرد")]],
					resize_keyboard=True,
					one_time_keyboard=True,
				)
				await event.answer("جنسیت خود را انتخاب کنید:", reply_markup=keyboard)
				return None

			# Step 2: gender
			if profile.is_female is None:
				if user.step != "ask_gender":
					user.step = "ask_gender"
					await session.commit()
					keyboard = ReplyKeyboardMarkup(
						keyboard=[[KeyboardButton(text="زن"), KeyboardButton(text="مرد")]],
						resize_keyboard=True,
						one_time_keyboard=True,
					)
					await event.answer("جنسیت خود را انتخاب کنید:", reply_markup=keyboard)
					return None
				normalized = text.lower()
				if normalized in {"زن", "زنانه", "female", "f"}:
					profile.is_female = True
				elif normalized in {"مرد", "آقا", "male", "m"}:
					profile.is_female = False
				else:
					await event.answer("پاسخ نامعتبر. ‘زن’ یا ‘مرد’ را انتخاب کنید.")
					return None
				# Next: ask age
				user.step = "ask_age"
				await session.commit()
				rows: list[list[KeyboardButton]] = []
				row: list[KeyboardButton] = []
				for n in range(1, 100):
					row.append(KeyboardButton(text=str(n)))
					if len(row) == 10:
						rows.append(row)
						row = []
				if row:
					rows.append(row)
				kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
				await event.answer("سن خود را انتخاب کنید:", reply_markup=kb)
				return None

			# Step 3: age
			if profile.age is None:
				if user.step != "ask_age":
					user.step = "ask_age"
					await session.commit()
					rows: list[list[KeyboardButton]] = []
					row: list[KeyboardButton] = []
					for n in range(1, 100):
						row.append(KeyboardButton(text=str(n)))
						if len(row) == 10:
							rows.append(row)
							row = []
					if row:
						rows.append(row)
					kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
					await event.answer("سن خود را انتخاب کنید:", reply_markup=kb)
					return None
				if not text.isdigit():
					await event.answer("لطفاً یک عدد بین 1 تا 99 انتخاب کنید.")
					return None
				age_val = int(text)
				if age_val < 1 or age_val > 99:
					await event.answer("عدد وارد شده باید بین 1 تا 99 باشد.")
					return None
				profile.age = age_val
				user.step = "ask_state"
				await session.commit()
				# Prompt states list
				states: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
				if not states:
					# No states available; skip profile flow
					data["profile_ok"] = True
					return await handler(event, data)
				rows: list[list[KeyboardButton]] = []
				row: list[KeyboardButton] = []
				for s in states:
					row.append(KeyboardButton(text=s.state_name))
					if len(row) == 3:
						rows.append(row)
						row = []
				if row:
					rows.append(row)
				kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
				await event.answer("استان خود را انتخاب کنید:", reply_markup=kb)
				return None

			# Step 4: state
			if profile.state is None:
				if user.step != "ask_state":
					user.step = "ask_state"
					await session.commit()
					# Re-show states
					states: List[State] = list(await session.scalars(select(State).order_by(State.state_name)))
					rows: list[list[KeyboardButton]] = []
					row: list[KeyboardButton] = []
					for s in states:
						row.append(KeyboardButton(text=s.state_name))
						if len(row) == 3:
							rows.append(row)
							row = []
					if row:
						rows.append(row)
					kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
					await event.answer("استان خود را انتخاب کنید:", reply_markup=kb)
					return None
				# Match state
				state: State | None = await session.scalar(
					select(State).where(State.state_name == text)
				)
				if state is None:
					await event.answer("استان نامعتبر است. از لیست انتخاب کنید.")
					return None
				profile.state = state.id
				user.step = "ask_city"
				await session.commit()
				# Prompt cities for the state
				cities: List[City] = list(
					await session.scalars(select(City).where(City.state_id == state.id).order_by(City.city_name))
				)
				if not cities:
					# No cities; finish
					user.step = "start"
					await session.commit()
					await event.answer("پروفایل تکمیل شد.", reply_markup=ReplyKeyboardRemove())
					data["profile_ok"] = True
					return await handler(event, data)
				rows: list[list[KeyboardButton]] = []
				row: list[KeyboardButton] = []
				for c in cities:
					row.append(KeyboardButton(text=c.city_name))
					if len(row) == 3:
						rows.append(row)
						row = []
				if row:
					rows.append(row)
				kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
				await event.answer("شهر خود را انتخاب کنید:", reply_markup=kb)
				return None

			# Step 4: city
			if profile.city is None:
				if user.step != "ask_city":
					user.step = "ask_city"
					await session.commit()
					await event.answer("شهر خود را انتخاب کنید:")
					return None
				state_id = profile.state
				if not state_id:
					await event.answer("ابتدا استان را انتخاب کنید.")
					return None
				city: City | None = await session.scalar(
					select(City).where(City.state_id == state_id, City.city_name == text)
				)
				if city is None:
					await event.answer("شهر نامعتبر است. از لیست انتخاب کنید.")
					return None
				profile.city = city.id
				user.step = "start"
				await session.commit()
				await event.answer("پروفایل تکمیل شد.", reply_markup=ReplyKeyboardRemove())
				data["profile_ok"] = True
				return await handler(event, data)

		# Profile already complete or nothing to do
		data["profile_ok"] = True
		return await handler(event, data)


