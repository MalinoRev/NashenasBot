from aiogram.types import CallbackQuery
from datetime import datetime, timedelta, timezone
from src.core.database import get_session
from src.databases.users import User
from src.databases.chats import Chat
from src.databases.directs import Direct
from src.databases.payments import Payment
from sqlalchemy import select, func, desc
from src.context.messages.replies.statistics_welcome import get_message as get_statistics_welcome_message
from src.context.keyboards.inline.statistics_main_menu import build_keyboard as build_statistics_main_kb
from src.context.messages.replies.statistics_table_menu import get_message as get_statistics_table_message
from src.context.keyboards.inline.statistics_table_menu import build_keyboard as build_statistics_table_kb
from src.context.messages.replies.statistics_comparison_menu import get_message as get_statistics_comparison_message
from src.context.keyboards.inline.statistics_comparison_menu import build_keyboard as build_statistics_comparison_kb
from src.context.messages.replies.statistics_new_users import get_message as get_new_users_message
from src.context.messages.replies.statistics_chats_opened import get_message as get_chats_opened_message
from src.context.messages.replies.statistics_directs_sent import get_message as get_directs_sent_message
from src.context.messages.replies.statistics_transactions_opened import get_message as get_transactions_opened_message
from src.context.messages.replies.statistics_referrals import get_message as get_referrals_message
from src.context.messages.replies.statistics_top_successful_transactions import get_message as get_top_successful_transactions_message
from src.context.messages.replies.statistics_top_transaction_amounts import get_message as get_top_transaction_amounts_message
from src.context.keyboards.inline.statistics_back import build_keyboard as build_statistics_back_kb


async def handle_statistics_callbacks(callback: CallbackQuery) -> None:
	"""Handle statistics callbacks"""
	data = callback.data or ""
	if not data.startswith("statistics:"):
		await callback.answer()
		return

	action = data.split(":", 1)[1]
	
	if action == "table":
		# Show statistics table menu
		await callback.message.edit_text(
			get_statistics_table_message(),
			reply_markup=build_statistics_table_kb(),
			parse_mode="Markdown"
		)
		await callback.answer()
		return
	
	if action == "comparison":
		# Show statistics comparison menu
		await callback.message.edit_text(
			get_statistics_comparison_message(),
			reply_markup=build_statistics_comparison_kb(),
			parse_mode="Markdown"
		)
		await callback.answer()
		return
	
	if action == "back":
		# Return to main statistics menu
		await callback.message.edit_text(
			get_statistics_welcome_message(),
			reply_markup=build_statistics_main_kb(),
			parse_mode="Markdown"
		)
		await callback.answer()
		return
	
	# Handle specific statistics actions
	if action in [
		"new_users", "chats_opened", "directs_sent", "transactions_opened", 
		"coins_spent", "referrals"
	]:
		await _handle_table_statistics(callback, action)
		return
	
	if action in [
		"top_successful_transactions", "top_transaction_amounts", "top_referrers",
		"top_coin_spenders", "top_direct_senders", "top_direct_receivers",
		"top_chat_senders", "top_chat_receivers", "top_likes", "top_likers"
	]:
		await _handle_comparison_statistics(callback, action)
		return
	
	await callback.answer()


async def _handle_table_statistics(callback: CallbackQuery, action: str) -> None:
	"""Handle table statistics display"""
	if action == "new_users":
		await _show_new_users_statistics(callback)
		return
	
	if action == "chats_opened":
		await _show_chats_opened_statistics(callback)
		return
	
	if action == "directs_sent":
		await _show_directs_sent_statistics(callback)
		return
	
	if action == "transactions_opened":
		await _show_transactions_opened_statistics(callback)
		return
	
	if action == "referrals":
		await _show_referrals_statistics(callback)
		return
	
	# Placeholder for other statistics - will be implemented based on user requirements
	await callback.answer("🔧 این بخش در حال توسعه است...", show_alert=True)


async def _show_new_users_statistics(callback: CallbackQuery) -> None:
	"""Show new users statistics for 24h, 7d, 30d"""
	now = datetime.now(timezone.utc)
	time_24h = now - timedelta(hours=24)
	time_7d = now - timedelta(days=7)
	time_30d = now - timedelta(days=30)
	
	async with get_session() as session:
		# Count users created in each time period
		count_24h = await session.scalar(
			select(func.count(User.id)).where(User.created_at >= time_24h)
		) or 0
		
		count_7d = await session.scalar(
			select(func.count(User.id)).where(User.created_at >= time_7d)
		) or 0
		
		count_30d = await session.scalar(
			select(func.count(User.id)).where(User.created_at >= time_30d)
		) or 0
		
		# Count total users
		total = await session.scalar(
			select(func.count(User.id))
		) or 0
	
	# Format and send the statistics
	text = get_new_users_message(count_24h, count_7d, count_30d, total)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()


async def _show_chats_opened_statistics(callback: CallbackQuery) -> None:
	"""Show opened chats statistics for 24h, 7d, 30d"""
	now = datetime.now(timezone.utc)
	time_24h = now - timedelta(hours=24)
	time_7d = now - timedelta(days=7)
	time_30d = now - timedelta(days=30)
	
	async with get_session() as session:
		# Count chats created in each time period
		count_24h = await session.scalar(
			select(func.count(Chat.id)).where(Chat.created_at >= time_24h)
		) or 0
		
		count_7d = await session.scalar(
			select(func.count(Chat.id)).where(Chat.created_at >= time_7d)
		) or 0
		
		count_30d = await session.scalar(
			select(func.count(Chat.id)).where(Chat.created_at >= time_30d)
		) or 0
		
		# Count total chats
		total = await session.scalar(
			select(func.count(Chat.id))
		) or 0
	
	# Format and send the statistics
	text = get_chats_opened_message(count_24h, count_7d, count_30d, total)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()


async def _show_directs_sent_statistics(callback: CallbackQuery) -> None:
	"""Show sent directs statistics for 24h, 7d, 30d"""
	now = datetime.now(timezone.utc)
	time_24h = now - timedelta(hours=24)
	time_7d = now - timedelta(days=7)
	time_30d = now - timedelta(days=30)
	
	async with get_session() as session:
		# Count directs created in each time period
		count_24h = await session.scalar(
			select(func.count(Direct.id)).where(Direct.created_at >= time_24h)
		) or 0
		
		count_7d = await session.scalar(
			select(func.count(Direct.id)).where(Direct.created_at >= time_7d)
		) or 0
		
		count_30d = await session.scalar(
			select(func.count(Direct.id)).where(Direct.created_at >= time_30d)
		) or 0
		
		# Count total directs
		total = await session.scalar(
			select(func.count(Direct.id))
		) or 0
	
	# Format and send the statistics
	text = get_directs_sent_message(count_24h, count_7d, count_30d, total)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()


async def _show_transactions_opened_statistics(callback: CallbackQuery) -> None:
	"""Show opened transactions statistics for 24h, 7d, 30d"""
	now = datetime.now(timezone.utc)
	time_24h = now - timedelta(hours=24)
	time_7d = now - timedelta(days=7)
	time_30d = now - timedelta(days=30)
	
	async with get_session() as session:
		# Count transactions created in each time period
		count_24h = await session.scalar(
			select(func.count(Payment.id)).where(Payment.created_at >= time_24h)
		) or 0
		
		count_7d = await session.scalar(
			select(func.count(Payment.id)).where(Payment.created_at >= time_7d)
		) or 0
		
		count_30d = await session.scalar(
			select(func.count(Payment.id)).where(Payment.created_at >= time_30d)
		) or 0
		
		# Count total transactions
		total = await session.scalar(
			select(func.count(Payment.id))
		) or 0
	
	# Format and send the statistics
	text = get_transactions_opened_message(count_24h, count_7d, count_30d, total)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()


async def _show_referrals_statistics(callback: CallbackQuery) -> None:
	"""Show referred users statistics for 24h, 7d, 30d"""
	now = datetime.now(timezone.utc)
	time_24h = now - timedelta(hours=24)
	time_7d = now - timedelta(days=7)
	time_30d = now - timedelta(days=30)
	
	async with get_session() as session:
		# Count users with referraled_by not null in each time period
		count_24h = await session.scalar(
			select(func.count(User.id)).where(
				User.created_at >= time_24h,
				User.referraled_by.isnot(None)
			)
		) or 0
		
		count_7d = await session.scalar(
			select(func.count(User.id)).where(
				User.created_at >= time_7d,
				User.referraled_by.isnot(None)
			)
		) or 0
		
		count_30d = await session.scalar(
			select(func.count(User.id)).where(
				User.created_at >= time_30d,
				User.referraled_by.isnot(None)
			)
		) or 0
		
		# Count total referred users
		total = await session.scalar(
			select(func.count(User.id)).where(User.referraled_by.isnot(None))
		) or 0
	
	# Format and send the statistics
	text = get_referrals_message(count_24h, count_7d, count_30d, total)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()


async def _show_top_transaction_amounts(callback: CallbackQuery) -> None:
	"""Show top 10 users with highest total transaction amounts"""
	async with get_session() as session:
		# Query to get users with highest total payment amounts (paid_at is not null)
		query = (
			select(User, func.sum(Payment.price).label('total_amount'))
			.join(Payment, User.id == Payment.user_id)
			.where(Payment.paid_at.isnot(None))
			.group_by(User.id)
			.order_by(desc('total_amount'))
			.limit(10)
		)
		
		result = await session.execute(query)
		transactions = result.fetchall()
	
	# Format and send the statistics
	text = get_top_transaction_amounts_message(transactions)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()


async def _handle_comparison_statistics(callback: CallbackQuery, action: str) -> None:
	"""Handle comparison statistics display"""
	if action == "top_successful_transactions":
		await _show_top_successful_transactions(callback)
		return
	
	if action == "top_transaction_amounts":
		await _show_top_transaction_amounts(callback)
		return
	
	# Placeholder for other comparison statistics - will be implemented based on user requirements
	await callback.answer("🔧 این بخش در حال توسعه است...", show_alert=True)


async def _show_top_successful_transactions(callback: CallbackQuery) -> None:
	"""Show top 10 users with most successful transactions"""
	async with get_session() as session:
		# Query to get users with most successful transactions (paid_at is not null)
		query = (
			select(User, func.count(Payment.id).label('successful_count'))
			.join(Payment, User.id == Payment.user_id)
			.where(Payment.paid_at.isnot(None))
			.group_by(User.id)
			.order_by(desc('successful_count'))
			.limit(10)
		)
		
		result = await session.execute(query)
		transactions = result.fetchall()
	
	# Format and send the statistics
	text = get_top_successful_transactions_message(transactions)
	kb = build_statistics_back_kb()
	
	await callback.message.edit_text(
		text,
		reply_markup=kb,
		parse_mode="Markdown"
	)
	await callback.answer()
