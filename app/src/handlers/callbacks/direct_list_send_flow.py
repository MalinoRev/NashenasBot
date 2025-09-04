from aiogram.types import CallbackQuery, LinkPreviewOptions
from sqlalchemy import select

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.callbacks.direct_prompt import get_message as get_direct_prompt
from src.context.keyboards.reply.special_contact import build_back_keyboard as build_back_kb
from src.context.keyboards.reply.mainButtons import build_keyboard_for
from src.context.messages.commands.start import get_message as get_start_message


def _parse_kind_page(data: str) -> tuple[str | None, int | None]:
    # data formats: direct_list_send_confirm:{kind}:{page}
    try:
        parts = data.split(":", 2)
        if len(parts) < 3:
            return None, None
        rest = parts[2]
        # rest contains kind and page separated by last colon if kind itself has colons (it shouldn't), but our builder used only one extra ':'
        # We built as f"...:{kind}:{page}" so split once from right
        kind, page_str = rest.rsplit(":", 1) if ":" in rest else (rest, "1")
        return kind, int(page_str)
    except Exception:
        return None, None


async def handle_direct_list_send_confirm(callback: CallbackQuery) -> None:
    data = callback.data or ""
    kind, page = _parse_kind_page(data)
    user_id = callback.from_user.id if callback.from_user else 0

    async with get_session() as session:
        user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            await callback.answer()
            return
        # Reset step like single direct confirm handler
        user.step = "start"
        await session.commit()

    # Acknowledge and show success, then /start
    try:
        await callback.message.edit_text("✅ پیام شما با موفقیت ذخیره شد و برای ارسال به لیست پردازش خواهد شد.")
    except Exception:
        await callback.message.answer("✅ پیام شما با موفقیت ذخیره شد و برای ارسال به لیست پردازش خواهد شد.")

    kb, _ = await build_keyboard_for(user_id)
    await callback.message.answer(
        get_start_message(callback.from_user.first_name if callback.from_user else None),
        reply_markup=kb,
        parse_mode="Markdown",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    await callback.answer()


async def handle_direct_list_send_cancel(callback: CallbackQuery) -> None:
    data = callback.data or ""
    kind, page = _parse_kind_page(data)
    user_id = callback.from_user.id if callback.from_user else 0

    async with get_session() as session:
        user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            await callback.answer()
            return
        user.step = "start"
        await session.commit()

    try:
        await callback.message.edit_text("❌ ارسال پیام به لیست لغو شد.")
    except Exception:
        await callback.message.answer("❌ ارسال پیام به لیست لغو شد.")

    kb, _ = await build_keyboard_for(user_id)
    await callback.message.answer(
        get_start_message(callback.from_user.first_name if callback.from_user else None),
        reply_markup=kb,
        parse_mode="Markdown",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    await callback.answer()


async def handle_direct_list_send_edit(callback: CallbackQuery) -> None:
    data = callback.data or ""
    kind, page = _parse_kind_page(data)
    if kind is None or page is None:
        await callback.answer()
        return
    user_id = callback.from_user.id if callback.from_user else 0

    async with get_session() as session:
        user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            await callback.answer()
            return
        # Set back to collecting message
        user.step = f"direct_list_{kind}_{page}"
        await session.commit()

    try:
        await callback.message.delete()
    except Exception:
        pass

    kb_back, _ = build_back_kb()
    await callback.message.answer(get_direct_prompt(), reply_markup=kb_back)
    await callback.answer()


