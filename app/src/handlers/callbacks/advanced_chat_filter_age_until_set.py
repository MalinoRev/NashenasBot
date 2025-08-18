from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.user_filters import UserFilter
from src.context.messages.callbacks.advanced_chat_filter_review import (
	format_message as format_review_message,
)
from src.context.keyboards.inline.advanced_chat_filter_review import (
	build_keyboard as build_review_keyboard,
)


async def handle_advanced_chat_filter_age_until_set(callback: CallbackQuery) -> None:
	data = callback.data or ""
	choice = data.split(":", 1)[1] if ":" in data else ""

	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
		if not user or user.step != "start":
			await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
			return

		uf: UserFilter | None = await session.scalar(select(UserFilter).where(UserFilter.user_id == user.id))
		if uf is None:
			uf = UserFilter(user_id=user.id)
			session.add(uf)

		if choice == "all":
			uf.age_until = None
		else:
			try:
				age_until = int(choice)
				uf.age_until = age_until
			except ValueError:
				pass

		await session.commit()

	# Build preview text from filters
	gender_text = "همه کاربران"
	if uf.only_males is True:
		gender_text = "فقط پسرها"
	elif uf.only_females is True:
		gender_text = "فقط دخترها"

	distance_text = ""
	if uf.same_state is True:
		distance_text = "هم استانی"
	elif uf.same_state is False:
		distance_text = "غیر هم استانی"
	elif uf.same_city is True:
		distance_text = "هم شهری"
	elif uf.same_city is False:
		distance_text = "غیر هم شهری"
	elif uf.distance_limit is not None:
		distance_text = f"تا {uf.distance_limit} کیلومتر"
	else:
		distance_text = "بدون محدودیت فاصله"

	if uf.age_from is None and uf.age_until is None:
		age_text = "بدون محدودیت سنی"
	else:
		from_age = uf.age_from if uf.age_from is not None else 1
		until_age = uf.age_until if uf.age_until is not None else 99
		age_text = f"از {from_age} تا {until_age} سال"

	preview = f"{gender_text} {distance_text} {age_text} می توانند به این کاربر درخواست چت بدهند."

	try:
		await callback.message.delete()
	except Exception:
		pass
	await callback.message.answer(
		format_review_message(preview), reply_markup=build_review_keyboard()
	)
	await callback.answer()


