from aiogram.types import CallbackQuery
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func

from src.core.database import get_session
from src.databases.payments import Payment


def _format_currency(amount: int) -> str:
	return f"{amount:,} تومان"


async def handle_financial_callbacks(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not data.startswith("financial:"):
		await callback.answer()
		return

	action = data.split(":", 1)[1]
	if action == "stats":
		# Compute sums for 24h, 7d, 30d over paid payments
		now = datetime.now(timezone.utc)
		w24 = now - timedelta(hours=24)
		w7 = now - timedelta(days=7)
		w30 = now - timedelta(days=30)
		async with get_session() as session:
			q = select(func.coalesce(func.sum(Payment.price), 0)).where(Payment.paid_at.is_not(None))
			last_24h = int(await session.scalar(q.where(Payment.paid_at >= w24)) or 0)
			last_7d = int(await session.scalar(q.where(Payment.paid_at >= w7)) or 0)
			last_30d = int(await session.scalar(q.where(Payment.paid_at >= w30)) or 0)
		text = (
			"📈 آمار کلی درآمد\n\n"
			f"▫️ 24 ساعت اخیر: {_format_currency(last_24h)}\n"
			f"▫️ 7 روز اخیر: {_format_currency(last_7d)}\n"
			f"▫️ 30 روز اخیر: {_format_currency(last_30d)}"
		)
		try:
			await callback.message.edit_text(text, parse_mode="Markdown")
		except Exception:
			await callback.message.answer(text, parse_mode="Markdown")
		await callback.answer()
		return

	# Placeholder for other actions
	await callback.answer()


