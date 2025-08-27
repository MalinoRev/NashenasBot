import os
import tempfile
import aiofiles
from pathlib import Path
from typing import Union, Optional, Dict, Any
from aiogram import Bot
from aiogram.types import Message, PhotoSize, Video, Animation, Audio, Document, Sticker, FSInputFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.media import Media


class CacheService:
    """Service for caching media files in Telegram channel instead of local storage"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache_channel_id = int(os.getenv('CACHE_CHANNEL_ID', '0'))

        # Ensure temp directory exists
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    async def test_cache_channel_access(self) -> Dict[str, Any]:
        """
        Test if bot has access to cache channel

        Returns:
            dict: Test results with status and details
        """
        result = {
            'channel_id': self.cache_channel_id,
            'is_set': self.cache_channel_id != 0,
            'has_access': False,
            'error': None,
            'channel_info': None
        }

        if not result['is_set']:
            result['error'] = 'CACHE_CHANNEL_ID not set'
            return result

        try:
            # Try to get chat information
            chat = await self.bot.get_chat(self.cache_channel_id)
            result['has_access'] = True
            result['channel_info'] = {
                'title': getattr(chat, 'title', 'Unknown'),
                'type': getattr(chat, 'type', 'Unknown'),
                'username': getattr(chat, 'username', None)
            }

            # Try to send a test message
            test_message = await self.bot.send_message(
                chat_id=self.cache_channel_id,
                text="Test message for cache channel access"
            )

            # Delete the test message
            await self.bot.delete_message(
                chat_id=self.cache_channel_id,
                message_id=test_message.message_id
            )

            result['can_send_messages'] = True

        except Exception as e:
            result['error'] = str(e)
            result['has_access'] = False
            result['can_send_messages'] = False

        return result

    async def save_media(self, media: Union[Message, PhotoSize, Video, Animation, Audio, Document, Sticker]) -> Optional[int]:
        """
        Save media to cache channel and return media_id

        Args:
            media: Media object from aiogram

        Returns:
            media_id: Unique identifier for the cached media, or None if failed
        """
        print(f"DEBUG: CacheService.save_media called with cache_channel_id={self.cache_channel_id}")

        if not self.cache_channel_id or str(self.cache_channel_id) == '0':
            print(f"ERROR: CACHE_CHANNEL_ID not set (value: '{os.getenv('CACHE_CHANNEL_ID', 'NOT_SET')}'), skipping media caching")
            return None

        print(f"DEBUG: Media type: {type(media)}")

        try:
            # Send media to cache channel
            sent_message = None

            if isinstance(media, Message):
                print(f"DEBUG: Forwarding message from chat {media.chat.id}, message {media.message_id}")
                # Forward the entire message with media
                sent_message = await self.bot.forward_message(
                    chat_id=self.cache_channel_id,
                    from_chat_id=media.chat.id,
                    message_id=media.message_id
                )
                print(f"DEBUG: Message forwarded successfully, sent_message_id={sent_message.message_id if sent_message else None}")
            else:
                # Handle different media types
                if hasattr(media, 'file_id'):
                    file_id = media.file_id
                    caption = getattr(media, 'caption', None)
                    print(f"DEBUG: Processing media with file_id={file_id[:20]}..., caption={caption}")

                    if isinstance(media, PhotoSize):
                        print(f"DEBUG: Sending photo to cache channel with caption='{caption}'")
                        sent_message = await self.bot.send_photo(
                            chat_id=self.cache_channel_id,
                            photo=file_id,
                            caption=caption if caption else None  # Don't send empty caption
                        )
                    elif isinstance(media, Video):
                        print(f"DEBUG: Sending video to cache channel with caption='{caption}'")
                        sent_message = await self.bot.send_video(
                            chat_id=self.cache_channel_id,
                            video=file_id,
                            caption=caption if caption else None  # Don't send empty caption
                        )
                    elif isinstance(media, Animation):
                        print(f"DEBUG: Sending animation to cache channel with caption='{caption}'")
                        sent_message = await self.bot.send_animation(
                            chat_id=self.cache_channel_id,
                            animation=file_id,
                            caption=caption if caption else None  # Don't send empty caption
                        )
                    elif isinstance(media, Audio):
                        print(f"DEBUG: Sending audio to cache channel with caption='{caption}'")
                        sent_message = await self.bot.send_audio(
                            chat_id=self.cache_channel_id,
                            audio=file_id,
                            caption=caption if caption else None  # Don't send empty caption
                        )
                    elif isinstance(media, Document):
                        print(f"DEBUG: Sending document to cache channel with caption='{caption}'")
                        sent_message = await self.bot.send_document(
                            chat_id=self.cache_channel_id,
                            document=file_id,
                            caption=caption if caption else None  # Don't send empty caption
                        )
                    elif isinstance(media, Sticker):
                        print("DEBUG: Sending sticker to cache channel")
                        sent_message = await self.bot.send_sticker(
                            chat_id=self.cache_channel_id,
                            sticker=file_id
                        )
                    else:
                        print(f"DEBUG: Unknown media type: {type(media)}")

            if sent_message:
                print(f"DEBUG: Media sent to cache channel, message_id={sent_message.message_id}")
                # Save message_id to database and return media_id
                async with get_session() as session:
                    print("DEBUG: Saving media record to database")
                    media_record = Media(message_id=sent_message.message_id)
                    session.add(media_record)
                    await session.commit()
                    await session.refresh(media_record)
                    print(f"DEBUG: Media record saved with id={media_record.id}")
                    return media_record.id
            else:
                print("ERROR: sent_message is None")

        except Exception as e:
            print(f"ERROR: Exception in save_media: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def send_media_to_user(self, media_id: int, chat_id: int) -> bool:
        """
        Copy media from cache channel to user (not forward, to avoid forward mark)

        Args:
            media_id: Unique identifier of the cached media
            chat_id: User's chat ID to send media to

        Returns:
            bool: True if successfully copied, False otherwise
        """
        print(f"DEBUG: CacheService.send_media_to_user called with media_id={media_id}, chat_id={chat_id}")

        try:
            async with get_session() as session:
                # Get media record from database
                print(f"DEBUG: Querying database for media_id={media_id}")
                result = await session.scalar(
                    select(Media).where(Media.id == media_id)
                )

                if not result:
                    print(f"ERROR: No media record found for media_id={media_id}")
                    return False

                print(f"DEBUG: Found media record with message_id={result.message_id}")

                # Copy message from cache channel to user (not forward)
                try:
                    print(f"DEBUG: Copying message from cache channel {self.cache_channel_id} to user {chat_id}")
                    await self.bot.copy_message(
                        chat_id=chat_id,
                        from_chat_id=self.cache_channel_id,
                        message_id=result.message_id
                    )

                    print(f"DEBUG: Successfully copied media to user")
                    return True

                except Exception as e:
                    print(f"ERROR: Failed to copy message from cache channel: {e}")
                    import traceback
                    traceback.print_exc()
                    return False

        except Exception as e:
            print(f"ERROR: Exception in send_media_to_user: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def send_media_with_caption(self, media_id: int, chat_id: int, caption: str) -> bool:
        """
        Copy media from cache channel to user and update caption

        Args:
            media_id: Unique identifier of the cached media
            chat_id: User's chat ID to send media to
            caption: Custom caption to use instead of original

        Returns:
            bool: True if successfully sent, False otherwise
        """
        print(f"DEBUG: CacheService.send_media_with_caption called with media_id={media_id}, chat_id={chat_id}, caption='{caption}'")

        try:
            async with get_session() as session:
                # Get media record from database
                print(f"DEBUG: Querying database for media_id={media_id}")
                result = await session.scalar(
                    select(Media).where(Media.id == media_id)
                )

                if not result:
                    print(f"ERROR: No media record found for media_id={media_id}")
                    return False

                print(f"DEBUG: Found media record with message_id={result.message_id}")

                # Copy message from cache channel to user
                try:
                    print(f"DEBUG: Copying message from cache channel {self.cache_channel_id} to user {chat_id}")

                    copied_message = await self.bot.copy_message(
                        chat_id=chat_id,
                        from_chat_id=self.cache_channel_id,
                        message_id=result.message_id
                    )

                    print(f"DEBUG: Message copied successfully, copied_message_id={copied_message.message_id if copied_message else None}")

                    # If we have a custom caption and it's different from empty, try to edit it
                    if caption and caption.strip():
                        print(f"DEBUG: Updating caption to: '{caption}'")

                        try:
                            # Try to edit caption - this works for media messages
                            await self.bot.edit_message_caption(
                                chat_id=chat_id,
                                message_id=copied_message.message_id,
                                caption=caption
                            )
                            print("DEBUG: Media caption updated successfully")

                        except Exception as e:
                            print(f"DEBUG: Could not edit caption: {e}")
                            # If caption editing fails, send a separate message with the caption
                            try:
                                await self.bot.send_message(
                                    chat_id=chat_id,
                                    text=f"💬 {caption}",
                                    reply_to_message_id=copied_message.message_id
                                )
                                print("DEBUG: Sent caption as separate message")
                            except Exception as e2:
                                print(f"ERROR: Could not send caption message: {e2}")

                    print(f"DEBUG: Successfully sent media with caption to user")
                    return True

                except Exception as e:
                    print(f"ERROR: Failed to copy message from cache channel: {e}")
                    import traceback
                    traceback.print_exc()
                    return False

        except Exception as e:
            print(f"ERROR: Exception in send_media_with_caption: {e}")
            import traceback
            traceback.print_exc()
            return False

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
