from aiogram.types import CallbackQuery
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, desc

from src.core.database import get_session
from src.databases.payments import Payment
from src.context.keyboards.inline.financial_pagination import build_keyboard as build_financial_pagination


def _format_currency(amount: int) -> str:
	return f"{amount:,} تومان"


def _get_filter_condition(filter_type: str):
	"""Get SQLAlchemy condition based on filter type"""
	if filter_type == "paid":
		return Payment.paid_at.isnot(None)
	elif filter_type == "unpaid":
		return Payment.paid_at.is_(None)
	else:  # "all"
		return None


def _get_next_filter(current_filter: str) -> str:
	"""Cycle through filter types: all -> paid -> unpaid -> all"""
	cycle = ["all", "paid", "unpaid"]
	try:
		current_idx = cycle.index(current_filter)
		return cycle[(current_idx + 1) % len(cycle)]
	except ValueError:
		return "all"


def _get_filter_display_name(filter_type: str) -> str:
	"""Get display name for filter type"""
	if filter_type == "paid":
		return "پرداخت شده ها"
	elif filter_type == "unpaid":
		return "پرداخت نشده ها"
	else:  # "all"
		return "همه"


async def _show_transactions_page(callback, page: int, filter_type: str) -> None:
	"""Show transactions page with filter applied"""
	page_size = 10
	filter_condition = _get_filter_condition(filter_type)
	
	async with get_session() as session:
		# Build query with filter
		query = select(Payment).order_by(desc(Payment.id))
		if filter_condition is not None:
			query = query.where(filter_condition)
		
		# Get items for current page
		items = list(await session.scalars(
			query.limit(page_size).offset((page - 1) * page_size)
		))
		has_next = len(items) == page_size
		
		# Boundary checks
		from src.context.alerts.search_bounds import get_first_page_message, get_last_page_message
		if page <= 1 and not items:
			# No transactions at all
			filter_text = f" ({_get_filter_display_name(filter_type)})" if filter_type != "all" else ""
			text = f"هیچ تراکنشی یافت نشد{filter_text}."
			kb = build_financial_pagination(page=page, has_next=False, page_size=page_size, filter_type=filter_type)
		elif not items and page > 1:
			# Trying to go beyond last page
			await callback.answer(get_last_page_message(), show_alert=True)
			return
		else:
			# Normal case - show items
			filter_text = f" ({_get_filter_display_name(filter_type)})" if filter_type != "all" else ""
			header = f"📜 تراکنش‌ها{filter_text} (جدیدترین تا قدیمی‌ترین)\n\n"
			rows = [ _format_tx_row(p) for p in items ]
			text = header + "\n".join(rows)
			kb = build_financial_pagination(page=page, has_next=has_next, page_size=page_size, filter_type=filter_type)
		
		try:
			await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
		except Exception:
			await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")


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
	
	# Handle filter toggle
	if action.startswith("filter_toggle:"):
		parts = action.split(":")
		current_filter = parts[1] if len(parts) > 1 else "all"
		page = int(parts[2]) if len(parts) > 2 else 1
		next_filter = _get_next_filter(current_filter)
		
		# Show transactions with new filter
		await _show_transactions_page(callback, page, next_filter)
		await callback.answer()
		return
	
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
		# First page with default filter
		await _show_transactions_page(callback, 1, "all")
		await callback.answer()
		return

	if data.startswith("financial_page:"):
		# financial_page:transactions:next:{current_page}:{filter_type}
		# financial_page:transactions:prev:{current_page}:{filter_type}
		parts = data.split(":")
		kind = parts[1] if len(parts) > 1 else ""
		direction = parts[2] if len(parts) > 2 else "next"
		curr_page_str = parts[3] if len(parts) > 3 else "1"
		filter_type = parts[4] if len(parts) > 4 else "all"
		try:
			curr_page = max(1, int(curr_page_str))
		except Exception:
			curr_page = 1
		page = curr_page + 1 if direction == "next" else curr_page - 1
		if page < 1:
			from src.context.alerts.search_bounds import get_first_page_message
			await callback.answer(get_first_page_message(), show_alert=True)
			return
		
		await _show_transactions_page(callback, page, filter_type)
		await callback.answer()
		return

	# Placeholder for other actions
	await callback.answer()


