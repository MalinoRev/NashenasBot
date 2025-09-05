from aiogram.types import Message
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select
import os


async def show_support_management(message: Message) -> None:
	# Super admin only
	user_id = message.from_user.id if message.from_user else 0
	is_super_admin = False
	try:
		admin_env = os.getenv("TELEGRAM_ADMIN_USER_ID")
		if user_id and admin_env and str(user_id) == str(admin_env):
			is_super_admin = True
	except Exception:
		is_super_admin = False
	if not is_super_admin:
		await message.answer("❌ فقط سوپر ادمین‌ها می‌توانند پشتیبان‌ها را مدیریت کنند.")
		return

	# Ensure step is admin_panel
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_panel":
			await message.answer("❌ شما در پنل مدیریت نیستید.")
			return

	from src.services.supporter_list_service import get_supporters_list
	from src.context.messages.replies.support_management_welcome import get_message as get_support_message
	from src.context.keyboards.inline.support_management_menu import build_keyboard as build_support_kb

	supporters_list = await get_supporters_list()
	await message.answer(get_support_message(supporters_list), reply_markup=build_support_kb(), parse_mode="Markdown")


