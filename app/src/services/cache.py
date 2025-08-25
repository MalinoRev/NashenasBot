import os
from typing import Union, Optional
from aiogram import Bot
from aiogram.types import Message, InputFile, FSInputFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.media import Media


class CacheService:
	def __init__(self, bot: Bot):
		self.bot = bot
		self.cache_channel_id = int(os.getenv('CACHE_CHANNEL_ID', '-1001234567890'))

	async def store_media(self, media: Union[Message, InputFile, FSInputFile]) -> int:
		"""
		Store media in cache channel and return media.id
		
		Args:
			media: Message object, InputFile, or FSInputFile to store
			
		Returns:
			int: The media.id that can be used to retrieve the media later
		"""
		try:
			# Send media to cache channel
			if isinstance(media, Message):
				# Forward the message to cache channel
				cached_message = await self.bot.forward_message(
					chat_id=self.cache_channel_id,
					from_chat_id=media.chat.id,
					message_id=media.message_id
				)
				message_id = cached_message.message_id
			else:
				# Send file to cache channel
				cached_message = await self.bot.send_document(
					chat_id=self.cache_channel_id,
					document=media
				)
				message_id = cached_message.message_id

			# Store in database
			async with get_session() as session:
				media_record = Media(message_id=message_id)
				session.add(media_record)
				await session.flush()
				await session.commit()
				
				return media_record.id

		except Exception as e:
			# Log error and return None
			print(f"Error storing media in cache: {e}")
			return None

	async def get_media(self, media_id: int) -> Optional[Message]:
		"""
		Retrieve media from cache channel using media.id
		
		Args:
			media_id: The media.id from the database
			
		Returns:
			Message: The cached message containing the media, or None if not found
		"""
		try:
			async with get_session() as session:
				# Get message_id from database
				media_record: Media = await session.scalar(
					select(Media).where(Media.id == media_id)
				)
				
				if not media_record:
					return None

				# Get message from cache channel
				message = await self.bot.get_message(
					chat_id=self.cache_channel_id,
					message_id=media_record.message_id
				)
				
				return message

		except Exception as e:
			print(f"Error retrieving media from cache: {e}")
			return None

	async def delete_media(self, media_id: int) -> bool:
		"""
		Delete media from cache channel and database
		
		Args:
			media_id: The media.id to delete
			
		Returns:
			bool: True if successful, False otherwise
		"""
		try:
			async with get_session() as session:
				# Get message_id from database
				media_record: Media = await session.scalar(
					select(Media).where(Media.id == media_id)
				)
				
				if not media_record:
					return False

				# Delete from cache channel
				try:
					await self.bot.delete_message(
						chat_id=self.cache_channel_id,
						message_id=media_record.message_id
					)
				except Exception:
					# Message might already be deleted from channel
					pass

				# Delete from database
				await session.delete(media_record)
				await session.commit()
				
				return True

		except Exception as e:
			print(f"Error deleting media from cache: {e}")
			return False

	async def get_media_id(self, message: Message) -> Optional[int]:
		"""
		Get media.id for a message that was sent to cache channel
		
		Args:
			message: Message object from cache channel
			
		Returns:
			int: The media.id if found, None otherwise
		"""
		try:
			async with get_session() as session:
				# Find media record by message_id
				media_record: Media = await session.scalar(
					select(Media).where(Media.message_id == message.message_id)
				)
				
				return media_record.id if media_record else None

		except Exception as e:
			print(f"Error getting media ID: {e}")
			return None
