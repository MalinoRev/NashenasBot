import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.directs import Direct
from src.databases.users import User
from src.services.cache import CacheService


class DirectService:
    """Service for managing direct messages stored in database"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache_service = CacheService(bot)

    async def save_direct(self, user_id: int, target_id: int, message_data: Dict[str, Any]) -> Optional[int]:
        """
        Save a direct message to database

        Args:
            user_id: Sender's database ID
            target_id: Receiver's database ID
            message_data: Message data (message, type, media_id if exists)

        Returns:
            direct_id: Unique identifier of the saved direct message
        """
        try:
            async with get_session() as session:
                direct = Direct(
                    user_id=user_id,
                    target_id=target_id,
                    content=message_data
                )
                session.add(direct)
                await session.commit()
                await session.refresh(direct)
                return direct.id
        except Exception as e:
            print(f"Error saving direct message: {e}")
            return None

    async def get_direct(self, direct_id: int) -> Optional[Direct]:
        """
        Get a direct message by ID

        Args:
            direct_id: Unique identifier of the direct message

        Returns:
            Direct object or None if not found
        """
        try:
            async with get_session() as session:
                direct = await session.scalar(
                    select(Direct).where(Direct.id == direct_id)
                )
                return direct
        except Exception as e:
            print(f"Error getting direct message: {e}")
            return None

    async def get_unread_directs(self, user_id: int) -> List[Direct]:
        """
        Get all unread direct messages for a user

        Args:
            user_id: User's database ID

        Returns:
            List of unread Direct objects
        """
        try:
            async with get_session() as session:
                result = await session.scalars(
                    select(Direct)
                    .where(Direct.target_id == user_id)
                    .where(Direct.opened_at.is_(None))
                    .order_by(desc(Direct.created_at))
                )
                return list(result)
        except Exception as e:
            print(f"Error getting unread directs: {e}")
            return []

    async def mark_as_read(self, direct_id: int) -> bool:
        """
        Mark a direct message as read

        Args:
            direct_id: Unique identifier of the direct message

        Returns:
            bool: True if successfully marked as read
        """
        try:
            async with get_session() as session:
                direct = await session.scalar(
                    select(Direct).where(Direct.id == direct_id)
                )
                if direct and not direct.opened_at:
                    direct.opened_at = datetime.utcnow()
                    await session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error marking direct as read: {e}")
            return False

    async def send_notification_to_receiver(self, target_telegram_id: int, direct_id: int) -> bool:
        """
        Send notification to receiver about new direct message

        Args:
            target_telegram_id: Receiver's Telegram ID
            direct_id: Direct message ID

        Returns:
            bool: True if notification sent successfully
        """
        try:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="👁️ مشاهده پیام",
                        callback_data=f"direct_view:{direct_id}"
                    )]
                ]
            )

            await self.bot.send_message(
                chat_id=target_telegram_id,
                text="📩 شما یک پیام دایرکت جدید دریافت کرده‌اید!",
                reply_markup=keyboard
            )
            return True
        except Exception as e:
            print(f"Error sending direct notification: {e}")
            return False

    async def send_direct_to_user(self, direct_id: int, telegram_chat_id: int) -> bool:
        """
        Send direct message content to user

        Args:
            direct_id: Direct message ID
            telegram_chat_id: User's Telegram chat ID

        Returns:
            bool: True if message sent successfully
        """
        try:
            async with get_session() as session:
                # Get Direct with user relationship in the same session
                direct = await session.scalar(
                    select(Direct)
                    .where(Direct.id == direct_id)
                    .options(selectinload(Direct.user))  # Load user relationship
                )

                if not direct:
                    return False

                content = direct.content
                message_text = content.get('message', '')
                message_type = content.get('type', 'text')
                media_id = content.get('media_id')

                # Send header
                from src.context.messages.direct.received_header import format_message as _fmt_header
                sender_uid = direct.user.unique_id if direct.user and direct.user.unique_id else str(direct.user_id)
                await self.bot.send_message(
                    chat_id=telegram_chat_id,
                    text=_fmt_header(sender_uid)
                )

                # Send message based on type
                if message_type == 'text':
                    await self.bot.send_message(
                        chat_id=telegram_chat_id,
                        text=message_text
                    )
                elif message_type in ['image', 'video', 'animation', 'audio', 'document', 'sticker']:
                    if media_id:
                        # Send media with caption from database
                        success = await self.cache_service.send_media_with_caption(media_id, telegram_chat_id, message_text)
                        if not success:
                            # Fallback: send text message if media not available
                            await self.bot.send_message(
                                chat_id=telegram_chat_id,
                                text=f"❌ خطا در نمایش مدیا: {message_text}"
                            )
                    else:
                        # No media_id (CACHE_CHANNEL_ID not set), just send text
                        await self.bot.send_message(
                            chat_id=telegram_chat_id,
                            text=f"پیام مدیا: {message_text}"
                        )
                else:
                    await self.bot.send_message(
                        chat_id=telegram_chat_id,
                        text=f"پیام: {message_text}"
                    )

                # Mark as read within the same session
                if not direct.opened_at:
                    direct.opened_at = datetime.utcnow()
                    await session.commit()
                return True

        except Exception as e:
            print(f"Error sending direct to user: {e}")
            return False
