import os
from typing import Union, Optional
from aiogram import Bot
from aiogram.types import Message, InputFile, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.media import Media


class CacheService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache_channel_id = int(os.getenv("CACHE_CHANNEL_ID", ""))

    async def save_media(self, file_id: str, file_type: str = "document") -> Optional[int]:
        """
        ذخیره مدیا در کانال کش و بازگشت media.id

        Args:
            file_id: آی‌دی فایل تلگرام
            file_type: نوع فایل (photo, video, audio, document)

        Returns:
            media.id در صورت موفقیت، None در صورت خطا
        """
        try:
            # ارسال فایل به کانال کش
            if file_type == "photo":
                message = await self.bot.send_photo(
                    chat_id=self.cache_channel_id,
                    photo=file_id
                )
            elif file_type == "video":
                message = await self.bot.send_video(
                    chat_id=self.cache_channel_id,
                    video=file_id
                )
            elif file_type == "audio":
                message = await self.bot.send_audio(
                    chat_id=self.cache_channel_id,
                    audio=file_id
                )
            else:  # document or other
                message = await self.bot.send_document(
                    chat_id=self.cache_channel_id,
                    document=file_id
                )

            # ذخیره message_id در دیتابیس
            async with get_session() as session:
                media = Media(message_id=message.message_id)
                session.add(media)
                await session.commit()
                await session.refresh(media)
                return media.id

        except Exception as e:
            print(f"Error saving media to cache: {e}")
            return None

    async def get_media(self, media_id: int) -> Optional[dict]:
        """
        گرفتن اطلاعات مدیا با داشتن media.id

        Args:
            media_id: آی‌دی مدیا در دیتابیس

        Returns:
            دیکشنری شامل message_id و اطلاعات مدیا، None در صورت عدم وجود
        """
        try:
            async with get_session() as session:
                media = await session.scalar(select(Media).where(Media.id == media_id))
                if not media:
                    return None

                # گرفتن اطلاعات پیام از کانال کش
                message = await self.bot.get_message(
                    chat_id=self.cache_channel_id,
                    message_id=media.message_id
                )

                return {
                    "message_id": media.message_id,
                    "message": message,
                    "created_at": media.created_at
                }

        except Exception as e:
            print(f"Error getting media from cache: {e}")
            return None

    async def get_media_id_by_message_id(self, message_id: int) -> Optional[int]:
        """
        گرفتن media.id با داشتن message_id

        Args:
            message_id: آی‌دی پیام در کانال کش

        Returns:
            media.id در صورت وجود، None در صورت عدم وجود
        """
        try:
            async with get_session() as session:
                media = await session.scalar(select(Media).where(Media.message_id == message_id))
                return media.id if media else None

        except Exception as e:
            print(f"Error getting media_id by message_id: {e}")
            return None

    async def send_cached_media(self, chat_id: Union[int, str], media_id: int) -> bool:
        """
        ارسال مدیا کش شده به چت مشخص

        Args:
            chat_id: آی‌دی چتی که باید مدیا ارسال بشه
            media_id: آی‌دی مدیا در دیتابیس

        Returns:
            True در صورت موفقیت، False در صورت خطا
        """
        try:
            media_info = await self.get_media(media_id)
            if not media_info:
                return False

            message = media_info["message"]

            # ارسال مدیا بر اساس نوع
            if message.photo:
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.video:
                await self.bot.send_video(
                    chat_id=chat_id,
                    video=message.video.file_id,
                    caption=message.caption
                )
            elif message.audio:
                await self.bot.send_audio(
                    chat_id=chat_id,
                    audio=message.audio.file_id,
                    caption=message.caption
                )
            elif message.document:
                await self.bot.send_document(
                    chat_id=chat_id,
                    document=message.document.file_id,
                    caption=message.caption
                )
            else:
                return False

            return True

        except Exception as e:
            print(f"Error sending cached media: {e}")
            return False

    async def delete_media(self, media_id: int) -> bool:
        """
        حذف مدیا از کش و دیتابیس

        Args:
            media_id: آی‌دی مدیا در دیتابیس

        Returns:
            True در صورت موفقیت، False در صورت خطا
        """
        try:
            async with get_session() as session:
                media = await session.scalar(select(Media).where(Media.id == media_id))
                if not media:
                    return False

                # حذف پیام از کانال کش
                await self.bot.delete_message(
                    chat_id=self.cache_channel_id,
                    message_id=media.message_id
                )

                # حذف از دیتابیس
                await session.delete(media)
                await session.commit()
                return True

        except Exception as e:
            print(f"Error deleting media from cache: {e}")
            return False


# Global instance variable
_cache_service: Optional[CacheService] = None


def get_cache_service(bot: Optional[Bot] = None) -> CacheService:
    """Get the global cache service instance"""
    global _cache_service
    if _cache_service is None and bot is not None:
        _cache_service = CacheService(bot)
    return _cache_service


async def init_cache_service(bot: Bot) -> CacheService:
    """Initialize the cache service with bot instance"""
    global _cache_service
    _cache_service = CacheService(bot)
    return _cache_service
