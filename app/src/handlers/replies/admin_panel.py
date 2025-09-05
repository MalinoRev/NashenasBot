from typing import Optional
from src.context.messages.replies.admin_panel_welcome import get_message as get_welcome_message
from src.context.keyboards.reply.admin_panel import build_keyboard as build_admin_kb
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select


async def handle_admin_panel(user_telegram_id: int) -> dict[str, str]:
	"""
	Handle admin panel access
	
	Args:
		user_telegram_id: Admin's Telegram user ID
		
	Returns:
		dict with text and reply_markup keys
	"""
	# Set user step to admin_panel
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_telegram_id))
		if user:
			user.step = "admin_panel"
			await session.commit()
	
	text = get_welcome_message()
	kb, _ = build_admin_kb()
	
	return {
		"text": text,
		"reply_markup": kb
	}
