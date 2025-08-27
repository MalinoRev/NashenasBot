import os
from typing import Union, Optional, Dict, Any
from aiogram import Bot
from aiogram.types import Message, PhotoSize, Video, Animation, Audio, Document, Sticker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.media import Media


class CacheService:
    """Service for caching media files in Telegram channel instead of local storage"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache_channel_id = int(os.getenv('CACHE_CHANNEL_ID', '0'))

    async def save_media(self, media: Union[Message, PhotoSize, Video, Animation, Audio, Document, Sticker]) -> Optional[int]:
        """
        Save media to cache channel and return media_id

        Args:
            media: Media object from aiogram

        Returns:
            media_id: Unique identifier for the cached media, or None if failed
        """
        if not self.cache_channel_id:
            raise ValueError("CACHE_CHANNEL_ID environment variable is not set")

        try:
            # Send media to cache channel
            sent_message = None

            if isinstance(media, Message):
                # Forward the entire message with media
                sent_message = await self.bot.forward_message(
                    chat_id=self.cache_channel_id,
                    from_chat_id=media.chat.id,
                    message_id=media.message_id
                )
            else:
                # Handle different media types
                if hasattr(media, 'file_id'):
                    file_id = media.file_id
                    caption = getattr(media, 'caption', None)

                    if isinstance(media, PhotoSize):
                        sent_message = await self.bot.send_photo(
                            chat_id=self.cache_channel_id,
                            photo=file_id,
                            caption=caption
                        )
                    elif isinstance(media, Video):
                        sent_message = await self.bot.send_video(
                            chat_id=self.cache_channel_id,
                            video=file_id,
                            caption=caption
                        )
                    elif isinstance(media, Animation):
                        sent_message = await self.bot.send_animation(
                            chat_id=self.cache_channel_id,
                            animation=file_id,
                            caption=caption
                        )
                    elif isinstance(media, Audio):
                        sent_message = await self.bot.send_audio(
                            chat_id=self.cache_channel_id,
                            audio=file_id,
                            caption=caption
                        )
                    elif isinstance(media, Document):
                        sent_message = await self.bot.send_document(
                            chat_id=self.cache_channel_id,
                            document=file_id,
                            caption=caption
                        )
                    elif isinstance(media, Sticker):
                        sent_message = await self.bot.send_sticker(
                            chat_id=self.cache_channel_id,
                            sticker=file_id
                        )

            if sent_message:
                # Save message_id to database and return media_id
                async with get_session() as session:
                    media_record = Media(message_id=sent_message.message_id)
                    session.add(media_record)
                    await session.commit()
                    await session.refresh(media_record)
                    return media_record.id

        except Exception as e:
            print(f"Error saving media to cache: {e}")
            return None

    async def get_media(self, media_id: int) -> Optional[Dict[str, Any]]:
        """
        Get media data by media_id

        Args:
            media_id: Unique identifier of the cached media

        Returns:
            dict: Media data with message_id and media information, or None if not found
        """
        try:
            async with get_session() as session:
                # Get media record from database
                result = await session.scalar(
                    select(Media).where(Media.id == media_id)
                )

                if not result:
                    return None

                # Get message from cache channel
                try:
                    message = await self.bot.get_message(
                        chat_id=self.cache_channel_id,
                        message_id=result.message_id
                    )

                    return {
                        'media_id': media_id,
                        'message_id': result.message_id,
                        'message': message
                    }

                except Exception as e:
                    print(f"Error retrieving message from cache channel: {e}")
                    return None

        except Exception as e:
            print(f"Error getting media from cache: {e}")
            return None

    async def delete_media(self, media_id: int) -> bool:
        """
        Delete media from cache

        Args:
            media_id: Unique identifier of the cached media

        Returns:
            bool: True if successfully deleted, False otherwise
        """
        try:
            async with get_session() as session:
                # Get media record
                media_record = await session.scalar(
                    select(Media).where(Media.id == media_id)
                )

                if not media_record:
                    return False

                # Delete message from cache channel
                try:
                    await self.bot.delete_message(
                        chat_id=self.cache_channel_id,
                        message_id=media_record.message_id
                    )
                except Exception as e:
                    print(f"Error deleting message from cache channel: {e}")

                # Delete record from database
                await session.delete(media_record)
                await session.commit()

                return True

        except Exception as e:
            print(f"Error deleting media from cache: {e}")
            return False
