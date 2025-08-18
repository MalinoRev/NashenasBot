from aiogram.types import CallbackQuery
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.databases.states import State
from src.context.messages.profileMiddleware.chooseState import get_message as get_choose_state_message
from src.context.keyboards.reply.state import build_keyboard as build_state_kb


async def handle_profile_edit_state_city(callback: CallbackQuery) -> None:
    async with get_session() as session:
        user: User | None = await session.scalar(select(User).where(User.user_id == callback.from_user.id))
        if not user or user.step != "start":
            await callback.answer("این بخش فقط از منوی اصلی قابل انجام است.", show_alert=True)
            return

        user.step = "edit_state"
        await session.commit()

        states = list(await session.scalars(select(State).order_by(State.state_name)))
        state_kb, _ = build_state_kb([s.state_name for s in states]) if states else build_state_kb([])

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(get_choose_state_message(), reply_markup=state_kb)
    await callback.answer()


