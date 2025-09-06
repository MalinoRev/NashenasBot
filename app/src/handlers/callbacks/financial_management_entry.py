from aiogram.types import Message
from src.core.database import get_session
from src.databases.users import User
from sqlalchemy import select


async def show_financial_management(message: Message) -> None:
	# Ensure step is admin_panel
	user_id = message.from_user.id if message.from_user else 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
		if not user or user.step != "admin_panel":
			await message.answer("❌ شما در پنل مدیریت نیستید.")
			return

	from src.context.messages.replies.financial_management_welcome import get_message as get_financial_message
	from src.context.keyboards.inline.financial_management_menu import build_keyboard as build_financial_kb
	await message.answer(get_financial_message(), reply_markup=build_financial_kb(), parse_mode="Markdown")


