from aiogram.types import CallbackQuery
from src.context.messages.replies.statistics_welcome import get_message as get_statistics_welcome_message
from src.context.keyboards.inline.statistics_main_menu import build_keyboard as build_statistics_main_kb
from src.context.messages.replies.statistics_table_menu import get_message as get_statistics_table_message
from src.context.keyboards.inline.statistics_table_menu import build_keyboard as build_statistics_table_kb
from src.context.messages.replies.statistics_comparison_menu import get_message as get_statistics_comparison_message
from src.context.keyboards.inline.statistics_comparison_menu import build_keyboard as build_statistics_comparison_kb


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
	# Placeholder for now - will be implemented based on user requirements
	await callback.answer("🔧 این بخش در حال توسعه است...", show_alert=True)


async def _handle_comparison_statistics(callback: CallbackQuery, action: str) -> None:
	"""Handle comparison statistics display"""
	# Placeholder for now - will be implemented based on user requirements
	await callback.answer("🔧 این بخش در حال توسعه است...", show_alert=True)
