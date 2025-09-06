from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.chats import Chat
from src.databases.users import User
from sqlalchemy import select, desc
from src.context.keyboards.inline.chat_pagination import build_keyboard as build_chat_pagination


def _format_chat_row(chat: Chat, user1: User, user2: User) -> str:
	"""Format a single chat row for display"""
	is_active = chat.ended_at is None
	status = "🟢 فعال" if is_active else "🔴 اتمام یافته"
	created = chat.created_at.strftime("%Y-%m-%d %H:%M")
	ended = chat.ended_at.strftime("%Y-%m-%d %H:%M") if chat.ended_at else "—"
	
	return f"""💬 **چت #{chat.id}**
👤 کاربر 1: {user1.tg_name} (ID: {user1.user_id})
👤 کاربر 2: {user2.tg_name} (ID: {user2.user_id})
📅 تاریخ ایجاد: {created}
📅 تاریخ اتمام: {ended}
{status}
━━━━━━━━━━━━━━━━━━━━"""


async def _show_chats_page(callback: CallbackQuery, page: int, is_active: bool) -> None:
	"""Show chats page with pagination"""
	page_size = 10
	
	async with get_session() as session:
		# Build query based on active status
		if is_active:
			query = select(Chat).where(Chat.ended_at.is_(None)).order_by(desc(Chat.id))
		else:
			query = select(Chat).where(Chat.ended_at.isnot(None)).order_by(desc(Chat.id))
		
		# Get items for current page
		items = list(await session.scalars(
			query.limit(page_size).offset((page - 1) * page_size)
		))
		has_next = len(items) == page_size
		
		# Get user details for each chat
		chats_with_users = []
		for chat in items:
			user1 = await session.scalar(select(User).where(User.id == chat.user1_id))
			user2 = await session.scalar(select(User).where(User.id == chat.user2_id))
			if user1 and user2:
				chats_with_users.append((chat, user1, user2))
		
		# Format display
		status_text = "فعال" if is_active else "اتمام یافته"
		
		# Boundary checks
		from src.context.alerts.search_bounds import get_last_page_message
		if page <= 1 and not chats_with_users:
			# No chats at all
			text = f"هیچ چت {status_text}‌ای یافت نشد."
			kb = build_chat_pagination(page=page, has_next=False, page_size=page_size, is_active=is_active)
		elif not chats_with_users and page > 1:
			# Trying to go beyond last page
			await callback.answer(get_last_page_message(), show_alert=True)
			return
		else:
			# Normal case - show items
			header = f"💬 **چت‌های {status_text}** (جدیدترین تا قدیمی‌ترین)\n\n"
			rows = [_format_chat_row(chat, user1, user2) for chat, user1, user2 in chats_with_users]
			text = header + "\n\n".join(rows)
			kb = build_chat_pagination(page=page, has_next=has_next, page_size=page_size, is_active=is_active)
		
		try:
			await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
		except Exception:
			await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")


async def handle_chat_management_callbacks(callback: CallbackQuery) -> None:
	"""Handle chat management callbacks"""
	data = callback.data or ""
	if not data.startswith("chat_management:"):
		await callback.answer()
		return

	action = data.split(":", 1)[1]
	
	if action == "active":
		# Show active chats
		await _show_chats_page(callback, 1, True)
		await callback.answer()
		return
	
	if action == "completed":
		# Show completed chats
		await _show_chats_page(callback, 1, False)
		await callback.answer()
		return
	
	await callback.answer()


async def handle_chat_pagination(callback: CallbackQuery) -> None:
	"""Handle chat pagination callbacks"""
	data = callback.data or ""
	if not data.startswith("chat_page:"):
		await callback.answer()
		return

	# chat_page:next:{current_page}:{status}
	# chat_page:prev:{current_page}:{status}
	parts = data.split(":")
	direction = parts[1] if len(parts) > 1 else "next"
	curr_page_str = parts[2] if len(parts) > 2 else "1"
	status_param = parts[3] if len(parts) > 3 else "active"
	
	try:
		curr_page = max(1, int(curr_page_str))
	except Exception:
		curr_page = 1
	
	page = curr_page + 1 if direction == "next" else curr_page - 1
	if page < 1:
		from src.context.alerts.search_bounds import get_first_page_message
		await callback.answer(get_first_page_message(), show_alert=True)
		return
	
	# Check if the target page exists
	page_size = 10
	is_active = status_param == "active"
	
	async with get_session() as session:
		# Build query based on active status
		if is_active:
			query = select(Chat).where(Chat.ended_at.is_(None)).order_by(desc(Chat.id))
		else:
			query = select(Chat).where(Chat.ended_at.isnot(None)).order_by(desc(Chat.id))
		
		# Get items for current page
		items = list(await session.scalars(
			query.limit(page_size).offset((page - 1) * page_size)
		))
		
		# Boundary checks
		from src.context.alerts.search_bounds import get_last_page_message
		if not items and page > 1:
			# Trying to go beyond last page
			await callback.answer(get_last_page_message(), show_alert=True)
			return
		
		# Show the page
		await _show_chats_page(callback, page, is_active)
		await callback.answer()
