from pathlib import Path
from aiogram.types import CallbackQuery, FSInputFile

from src.context.messages.callbacks.coin_gateway_notice import get_caption as get_gateway_caption
from src.context.messages.callbacks.advanced_delete_account import get_prepare_message
from src.context.messages.callbacks.coin_buy import (
	get_intro_message as get_link_intro,
	get_link_message,
	get_error_message,
)
from src.services.payments.zarinpal import create_payment_link


async def handle_advanced_delete_account_pay(callback: CallbackQuery) -> None:
	# Show gateway notice image
	image_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "gateway.jpg"
	)
	try:
		photo = FSInputFile(image_path)
		await callback.message.answer_photo(photo, caption=get_gateway_caption())
	except Exception:
		pass

	# Show preparing message with price
	await callback.message.answer(get_prepare_message())

	# Build payment link (use product tag 'delete_account') with price from env
	import os
	price_toman = int(os.getenv("ACCOUNT_DELETE_PRICE", "0") or 0)
	user_id_tg = callback.from_user.id if callback.from_user else 0
	try:
		url = await create_payment_link(user_id_tg, price_toman, "delete_account")
	except Exception:
		await callback.message.answer(get_error_message())
		await callback.answer()
		return

	await callback.message.answer(get_link_intro())
	await callback.message.answer(get_link_message(url), parse_mode="Markdown")
	await callback.answer()


