from pathlib import Path
from aiogram.types import CallbackQuery, FSInputFile

from src.context.messages.callbacks.coin_gateway_notice import get_caption as get_gateway_caption
from src.context.messages.callbacks.coin_buy import (
	get_intro_message,
	get_link_message,
	get_error_message,
)
from src.context.messages.callbacks.coin_gateway_prepare import get_message as get_gateway_prepare
from src.services.payments.zarinpal import create_payment_link
from src.context.messages.callbacks.coin_vip_intro import get_message as get_vip_intro


async def handle_coin_buy_vip(callback: CallbackQuery) -> None:
	# Delete previous message if possible
	try:
		await callback.message.delete()
	except Exception:
		pass

	# Send VIP intro message first
	await callback.message.answer(get_vip_intro())

	# Show gateway notice image with caption
	image_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "gateway.jpg"
	)
	try:
		photo = FSInputFile(image_path)
		await callback.message.answer_photo(photo, caption=get_gateway_caption())
	except Exception:
		pass

	# Prepare message with VIP price (from DB)
	from sqlalchemy import select
	from src.core.database import get_session
	from src.databases.products import Product
	async with get_session() as session:
		product: Product | None = await session.scalar(select(Product))
		vip_price = int(getattr(product, "vip_rank_price", 0)) if product else 0
	await callback.message.answer(get_gateway_prepare(amount=0, price=vip_price))

	# Create payment link (product tag 'vip_rank')
	user_id_tg = callback.from_user.id if callback.from_user else 0
	try:
		url = await create_payment_link(user_id_tg, vip_price, "vip_rank")
	except Exception:
		await callback.message.answer(get_error_message())
		await callback.answer()
		return

	await callback.message.answer(get_intro_message())
	await callback.message.answer(get_link_message(url), parse_mode="Markdown")
	await callback.answer()


