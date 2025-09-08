import os
from pathlib import Path
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
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
from src.context.messages.callbacks.coin_gateway_notice import get_caption as get_gateway_caption
from src.context.messages.callbacks.coin_gateway_prepare import get_message as get_gateway_prepare


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

	# First, send gateway notice image with caption
	image_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "gateway.jpg"
	)
	try:
		photo = FSInputFile(image_path)
		await callback.message.answer_photo(photo, caption=get_gateway_caption())
	except Exception:
		pass

	# Inform user that link for this amount/price is being prepared
	await callback.message.answer(get_gateway_prepare(int(price.amount), int(price.price)))
	try:
		# Persist product as a machine-readable identifier for callback processing
		url = await create_payment_link(user_id_tg, int(price.price), f"coin:{price.amount}")
	except Exception:
		await callback.message.answer(get_error_message())
		await callback.answer()
		return

	await callback.message.answer(get_intro_message())
	
	# Create inline keyboard with payment link
	payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔗 باز پرداخت", url=url)]
	])
	
	await callback.message.answer(get_link_message(url), reply_markup=payment_keyboard, parse_mode="Markdown")
	await callback.answer()


