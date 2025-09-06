from aiogram.types import CallbackQuery
from sqlalchemy import select, update

from src.core.database import get_session
from src.databases.bot_settings import BotSetting
from src.databases.users import User


async def handle_maintenance_mode_toggle(callback: CallbackQuery) -> None:
    """Handle maintenance mode toggle buttons"""
    action = callback.data.split(":")[1]  # "normal" or "maintenance"
    
    async with get_session() as session:
        # Get current user
        user = await session.scalar(
            select(User).where(User.user_id == callback.from_user.id)
        )
        if not user:
            await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
            return
        
        # Get current bot settings
        settings = await session.scalar(select(BotSetting))
        if not settings:
            await callback.answer("❌ تنظیمات ربات یافت نشد.", show_alert=True)
            return
        
        # Update maintenance mode
        new_mode = action == "maintenance"
        await session.execute(
            update(BotSetting)
            .where(BotSetting.id == settings.id)
            .values(maintenance_mode=new_mode)
        )
        await session.commit()
        
        # Send success message
        mode_text = "تعمیرات" if new_mode else "عادی"
        status_emoji = "🔧" if new_mode else "🟢"
        
        await callback.message.edit_text(
            f"{status_emoji} حالت {mode_text} با موفقیت فعال شد!\n\n"
            f"وضعیت فعلی: {status_emoji} حالت {mode_text}",
            reply_markup=callback.message.reply_markup
        )
        
        await callback.answer(f"✅ حالت {mode_text} فعال شد")
