from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.prices import Price
from src.services.payments.zarinpal import create_payment_link
from src.context.messages.callbacks.coin_buy import (
	get_intro_message,
	get_link_message,
	get_error_message,
)


async def handle_coin_buy(callback: CallbackQuery) -> None:
	data = callback.data or ""
	parts = data.split(":", 2)
	if len(parts) != 3:
		await callback.answer()
		return
	_, _, raw_id = parts
	try:
		price_id = int(raw_id)
	except ValueError:
		await callback.answer()
		return

	user_id_tg = callback.from_user.id if callback.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id_tg))
		if not user:
			await callback.answer()
			return
		price: Price | None = await session.scalar(select(Price).where(Price.id == price_id))
		if not price:
			await callback.answer()
			return

	try:
		url = await create_payment_link(user_id_tg, int(price.price), f"خرید {price.amount} سکه")
	except Exception:
		await callback.message.answer(get_error_message())
		await callback.answer()
		return

	await callback.message.answer(get_intro_message())
	await callback.message.answer(get_link_message(url), parse_mode="Markdown")
	await callback.answer()


