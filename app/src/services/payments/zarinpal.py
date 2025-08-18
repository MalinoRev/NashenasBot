import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.payments import Payment


async def create_payment_link(user_id_tg: int, price_toman: int, product: str) -> str:
	"""
	Create a Zarinpal payment and return the redirect URL.

	Args:
		user_id_tg: Telegram user id
		price_toman: Price in Toman as stored in our `prices.price`
		product: A short product title/description

	Returns:
		Payment start URL that the user should be redirected to
	"""
	merchant_id = os.getenv("ZARINPAL_MERCHANT_ID")
	base_url = os.getenv("SITE_BASE_URL")
	sandbox_flag = (os.getenv("ZARINPAL_USE_SANDBOX", "false").lower() in {"1", "true", "yes"})
	if not merchant_id:
		raise RuntimeError("ZARINPAL_MERCHANT_ID is not set")
	if not base_url:
		raise RuntimeError("SITE_BASE_URL is not set")

	request_endpoint = (
		"https://sandbox.zarinpal.com/pg/v4/payment/request.json"
		if sandbox_flag
		else "https://payment.zarinpal.com/pg/v4/payment/request.json"
	)
	startpay_base = (
		"https://sandbox.zarinpal.com/pg/StartPay/"
		if sandbox_flag
		else "https://payment.zarinpal.com/pg/StartPay/"
	)

	amount_rial = int(price_toman) * 10

	async with get_session() as session:
		user: Optional[User] = await session.scalar(select(User).where(User.user_id == user_id_tg))
		if not user:
			raise RuntimeError("User not found")

		payment = Payment(
			user_id=user.id,
			price=price_toman,
			product=product,
			authority="",
		)
		session.add(payment)
		await session.flush()  # get payment.id

		callback_url = f"{base_url.rstrip('/')}/callback"
		payload = {
			"merchant_id": merchant_id,
			"amount": amount_rial,
			"callback_url": callback_url,
			"description": f"سفارش کاربر با آیدی {user_id_tg}",
		}

		async with httpx.AsyncClient(timeout=15.0) as client:
			resp = await client.post(request_endpoint, json=payload)
			resp.raise_for_status()
			data = resp.json()

			# Expected format: {"data": {"code": 100, "message": ..., "authority": "..."}, "errors": {...}}
			authority: Optional[str] = None
			try:
				if isinstance(data, dict) and "data" in data:
					inner = data["data"] or {}
					if inner.get("code") == 100:
						authority = inner.get("authority")
			except Exception as exc:  # noqa: BLE001
				raise RuntimeError("Invalid response from Zarinpal") from exc

			if not authority:
				raise RuntimeError("Failed to create payment request with Zarinpal")

			# Persist authority and expiry (Zarinpal authorities typically valid ~30 minutes)
			payment.authority = authority
			payment.expired_at = datetime.now(timezone.utc) + timedelta(minutes=30)
			await session.commit()

		return f"{startpay_base}{authority}"


