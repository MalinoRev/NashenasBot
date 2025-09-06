from aiogram.types import CallbackQuery
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, desc

from src.core.database import get_session
from src.databases.payments import Payment
from src.context.keyboards.inline.financial_pagination import build_keyboard as build_financial_pagination


def _format_currency(amount: int) -> str:
	return f"{amount:,} تومان"


def _format_tx_row(p: Payment) -> str:
	paid = p.paid_at.strftime("%Y-%m-%d %H:%M") if p.paid_at else "—"
	status = "✅ پرداخت شده" if p.paid_at else "❌ ناموفق/لغو"
	return (
		f"```\n"
		f"شناسه تراکنش: #{p.id}\n"
		f"آیدی کاربر: {p.user_id}\n"
		f"محصول: {p.product}\n"
		f"مبلغ: {p.price:,} تومان\n"
		f"وضعیت: {status}\n"
		f"تاریخ پرداخت: {paid}\n"
		f"```"
	)


async def handle_financial_callbacks(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if not (data.startswith("financial:") or data.startswith("financial_page:")):
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

	if action == "transactions":
		# First page
		page = 1
		page_size = 10
		async with get_session() as session:
			items = list(await session.scalars(
				select(Payment).order_by(desc(Payment.id)).limit(page_size).offset((page - 1) * page_size)
			))
			total_shown = len(items)
			has_next = total_shown == page_size
			if not items:
				text = "هیچ تراکنشی یافت نشد."
			else:
				header = "📜 تراکنش‌ها (جدیدترین تا قدیمی‌ترین)\n\n"
				rows = [ _format_tx_row(p) for p in items ]
				text = header + "\n".join(rows)
			kb = build_financial_pagination(page=page, has_next=has_next, page_size=page_size)
			try:
				await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
			except Exception:
				await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
		await callback.answer()
		return

	if data.startswith("financial_page:"):
		# financial_page:transactions:next:{current_page}
		# financial_page:transactions:prev:{current_page}
		parts = data.split(":")
		kind = parts[1] if len(parts) > 1 else ""
		direction = parts[2] if len(parts) > 2 else "next"
		curr_page_str = parts[3] if len(parts) > 3 else "1"
		try:
			curr_page = max(1, int(curr_page_str))
		except Exception:
			curr_page = 1
		page = curr_page + 1 if direction == "next" else curr_page - 1
		if page < 1:
			from src.context.alerts.search_bounds import get_first_page_message
			await callback.answer(get_first_page_message(), show_alert=True)
			return
		page_size = 10
		
		async with get_session() as session:
			items = list(await session.scalars(
				select(Payment).order_by(desc(Payment.id)).limit(page_size).offset((page - 1) * page_size)
			))
			has_next = len(items) == page_size
			
			# Boundary checks - only show alerts for invalid navigation
			from src.context.alerts.search_bounds import get_first_page_message, get_last_page_message
			if page <= 1 and not items:
				# No transactions at all
				text = "هیچ تراکنشی یافت نشد."
				kb = build_financial_pagination(page=page, has_next=False, page_size=page_size)
			elif page <= 1 and items:
				# On first page with items - check if trying to go to page 0
				if page < 1:
					await callback.answer(get_first_page_message(), show_alert=True)
					return
				# Normal first page
				header = "📜 تراکنش‌ها (جدیدترین تا قدیمی‌ترین)\n\n"
				rows = [ _format_tx_row(p) for p in items ]
				text = header + "\n".join(rows)
				kb = build_financial_pagination(page=page, has_next=has_next, page_size=page_size)
			elif not items and page > 1:
				# Trying to go beyond last page
				await callback.answer(get_last_page_message(), show_alert=True)
				return
			else:
				# Normal case - show items
				header = "📜 تراکنش‌ها (جدیدترین تا قدیمی‌ترین)\n\n"
				rows = [ _format_tx_row(p) for p in items ]
				text = header + "\n".join(rows)
				kb = build_financial_pagination(page=page, has_next=has_next, page_size=page_size)
			
			try:
				await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
			except Exception:
				await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
		await callback.answer()
		return

	# Placeholder for other actions
	await callback.answer()


