from aiogram.types import CallbackQuery
from src.core.database import get_session
from src.databases.users import User
from src.databases.user_bans import UserBan
from sqlalchemy import select, desc, and_


def _format_user_row(user: User, is_banned: bool = False) -> str:
	"""Format a single user row for display"""
	status = "🚫 مسدود شده" if is_banned else "✅ فعال"
	created = user.created_at.strftime("%Y-%m-%d %H:%M")
	
	return f"""👤 **کاربر #{user.id}**
📛 نام: {user.tg_name}
🆔 آیدی: {user.user_id}
📅 تاریخ عضویت: {created}
{status}
━━━━━━━━━━━━━━━━━━━━"""


async def _show_banned_users_page(callback: CallbackQuery, page: int) -> None:
	"""Show banned users page with pagination"""
	page_size = 10
	
	async with get_session() as session:
		# Build query for banned users using join with user_bans table
		query = select(User, UserBan).join(UserBan, User.id == UserBan.user_id).order_by(desc(UserBan.created_at))
		
		# Get items for current page
		items = list(await session.execute(
			query.limit(page_size).offset((page - 1) * page_size)
		))
		has_next = len(items) == page_size
		
		# Format display
		if not items:
			text = "هیچ کاربر مسدود شده‌ای یافت نشد."
		else:
			header = "🚫 **کاربران مسدود شده** (جدیدترین تا قدیمی‌ترین)\n\n"
			rows = [_format_user_row(user, is_banned=True) for user, ban in items]
			text = header + "\n\n".join(rows)
		
		# Build pagination keyboard
		from src.context.keyboards.inline.user_pagination import build_keyboard as build_user_pagination
		kb = build_user_pagination(page=page, has_next=has_next, page_size=page_size, user_type="banned")
		
		try:
			await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
		except Exception:
			await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")


async def handle_user_management_callbacks(callback: CallbackQuery) -> None:
	"""Handle user management callbacks"""
	data = callback.data or ""
	if not data.startswith("user_management:"):
		await callback.answer()
		return

	action = data.split(":", 1)[1]
	
	if action == "banned":
		# Show banned users
		await _show_banned_users_page(callback, 1)
		await callback.answer()
		return
	
	if action == "search":
		# Set user step to user_search
		from src.core.database import get_session
		from src.databases.users import User
		from sqlalchemy import select
		
		async with get_session() as session:
			user = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
			if user:
				user.step = "user_search"
				await session.commit()
		
		# Show search prompt
		from src.context.messages.replies.user_search_prompt import get_message as get_search_prompt
		from src.context.keyboards.reply.user_search_back import get_keyboard as get_search_back_keyboard
		
		await callback.message.delete()
		await callback.message.answer(
			get_search_prompt(),
			reply_markup=get_search_back_keyboard(),
			parse_mode="Markdown"
		)
		await callback.answer()
		return
	
		await callback.answer()


async def search_users(query: str) -> list[User]:
	"""Search users by username or user ID"""
	async with get_session() as session:
		# Try to search by user ID first (if query is numeric)
		if query.isdigit():
			user_id = int(query)
			users = list(await session.scalars(
				select(User).where(User.user_id == user_id)
			))
			if users:
				return users
		
		# Search by username (with or without @)
		username = query.lstrip('@')
		users = list(await session.scalars(
			select(User).where(User.tg_name.ilike(f"%{username}%"))
		))
		
		return users


async def handle_user_search(message, query: str) -> None:
	"""Handle user search and display results"""
	users = await search_users(query)
	
	if not users:
		from src.context.messages.replies.user_search_results import get_no_results_message
		await message.answer(get_no_results_message(), parse_mode="HTML")
		return
	
	# Check if user is banned
	user = users[0]
	async with get_session() as session:
		ban_record = await session.scalar(
			select(UserBan).where(UserBan.user_id == user.id)
		)
		is_banned = ban_record is not None
	
	# Format results
	from src.context.messages.replies.user_search_results import get_user_details
	text = get_user_details(user, is_banned)
	
	await message.answer(text, parse_mode="HTML")


async def handle_user_pagination(callback: CallbackQuery) -> None:
	"""Handle user pagination callbacks"""
	data = callback.data or ""
	if not data.startswith("user_page:"):
		await callback.answer()
		return

	# user_page:next:{current_page}:{user_type}
	# user_page:prev:{current_page}:{user_type}
	parts = data.split(":")
	direction = parts[1] if len(parts) > 1 else "next"
	curr_page_str = parts[2] if len(parts) > 2 else "1"
	user_type = parts[3] if len(parts) > 3 else "banned"
	
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
	
	async with get_session() as session:
		# Build query based on user type
		if user_type == "banned":
			query = select(User, UserBan).join(UserBan, User.id == UserBan.user_id).order_by(desc(UserBan.created_at))
		else:
			query = select(User).order_by(desc(User.id))
		
		# Get items for current page
		if user_type == "banned":
			items = list(await session.execute(
				query.limit(page_size).offset((page - 1) * page_size)
			))
		else:
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
		if user_type == "banned":
			await _show_banned_users_page(callback, page)
		else:
			# Handle other user types if needed
			pass
		
		await callback.answer()
